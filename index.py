#coding=utf-8
from flask import Flask, render_template,request
import markdown
from flask_flatpages import FlatPages

app = Flask(__name__)
pages = FlatPages(app)
app.config.from_pyfile("blog.conf", silent=True)

@app.route("/<path>.html")
def page(path):
    post = pages.get_or_404(path)
    html=markdown.markdown(post.body)
    pagetitle = post['title']
    return render_template('page.html', pagetitle=pagetitle,postcontent=html,post=post)

@app.route("/")
def index():
    pagesize=app.config.get("FLATPAGES_ROOT_SIZE",2)
    pp = request.args.get('p', '1')
    page = int(pp)
    if page<=0:
        page=1
    start = (page-1)*pagesize;
    end = page*pagesize;
    cate = request.args.get('cate', '')
    posts = [p for p in pages if(cate=='' or p['category']==cate)]
    total=len(posts)
    posts.sort(key=lambda item:item['date'], reverse=True)
    pagetitle=""
    if cate<> '':
        pagetitle=cate
    return render_template('index.html',pagetitle=pagetitle,posts=posts[start:end],totalnum=total)

@app.context_processor
def contextUtil():
    def renderNav():
        cates = [p['category'].strip() for p in pages if( 'category' in p.meta and p['category'] is not None) ]
        cates = list(set(cates))
        cates.sort()
        return render_template('nav.html',categories=cates,curcate = request.args.get('cate', ''))
    def getTags(tagstr):
        fixed_tags = tagstr.split(',')
        return [ tag.strip() for tag in fixed_tags]
    return dict(renderNav=renderNav,getTags=getTags)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8080,debug=True)