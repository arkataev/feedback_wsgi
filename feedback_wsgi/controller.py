from .response import success_json, render, restricted_json, page_not_found
from .request import Request
from . import database as db
import re

def validate_comment(func):
    errors = []
    required = ['last_name', 'first_name', 'email', 'comment', 'fam_name']
    valid_email = lambda email: re.search(r'^\S+@\D+\.[a-z]{2,}$', email)

    def validator(request:'Request'):
        if not request.valid_token: return restricted_json({'error': 'token mismatch'})
        missing = [i for i in required if not request.post.getvalue(i)]
        if missing: errors.extend([(f, 'required') for f in missing])
        if not valid_email(request.post.getvalue('email')): errors.append(('email','invalid'))
        return func(request) if not errors else restricted_json({'errors': dict(errors)})
    return validator

@validate_comment
def add_comment(request:'Request'):
    error = False
    message = 'Comment Saved!'
    user_fields = ['last_name', 'first_name', 'fam_name', 'phone', 'email', 'city']
    user_data = dict(zip(user_fields,[request.post.getvalue(field) for field in user_fields]))
    user_id = db.save_user(user_data)
    comment = request.post.getvalue('comment')
    if user_id: comment_id = db.save_comment(user_id, comment)
    if not user_id or not comment_id:
        error = True
        message = 'Sorry, error occured while saving new comment'
    return success_json({'error': error, 'message': message})

def comment(request:'Request', **kwargs):
    regions = dict(db.get_regions())
    html = ''
    for uid in regions:
        html += '<option id={id} value={id}>{text}</option>\n'.format(**{'id':uid, 'text':regions[uid]})
    kwargs.update({'regions': html})
    return render('comment.html', **kwargs)

def delete_comment(request:'Request'):
    db.delete_comment(request.post.getvalue('comment_id'))
    return success_json({'error':False, 'message': 'Comment Deleted'})

def view_stats(request:'Request'):
    stats = dict(db.get_stats())
    html = '';
    for s in stats:
        html += "<tr><td class='rname'><a href=/r_details>{region}</a></td>" \
                "<td class='count'>{count}</td></tr>".format(region=s,count = stats[s])
    return render('stats.html', rows=html)

def get_locations(request:'Request'):
    regions = dict(db.get_locations(request.post.getvalue('region_id')))
    return success_json(regions)

def not_found(request:'Request'):
    return page_not_found('not_found.html')

def view_comments(request:'request.Request'):
    comments = db.get_comments()
    html = ''
    for c in comments:
        html += '<li class="comment"><span class="user">{fname} {lname}</span><p>{comment}</p>' \
                '<button data-uid="{uid}">Удалить</button></li>\n'.format(
            fname=c[2], lname=c[3], comment=c[1], uid=c[0])
    return render('view.html', comments=html)