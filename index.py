#coding=utf-8
import codecs

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
    fixed_tags = post['tags'].split(',')
    fixed_tags = [ tag.strip() for tag in fixed_tags]
    pagetitle = post['title']
    return render_template('page.html', pagetitle=pagetitle,postcontent=html,page=post,fixed_tags=fixed_tags)

@app.route("/")
def index():
    pagesize=app.config.get("pagesize",2)
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
    return render_template('index.html',pagetitle=pagetitle,posts=posts[start:end],pnum=page,totalnum=total,cate=cate)

@app.context_processor
def contextUtil():
    def renderNav():
        cates = [p['category'].strip() for p in pages if( 'category' in p.meta and p['category'] is not None) ]
        cates = list(set(cates))
        cates.sort()
        return render_template('nav.html',categories=cates)
    def renderPager(cate,total,page):
        pagesize=app.config.get("pagesize",2)
        pager={}
        pager['cur']=page
        pager['former']=page-1
        pager['next']=page+1
        if total <= page*pagesize:
            pager['next']=0
        pager['total']=total
        pager['all']=total/pagesize
        if total%pagesize >0:
            pager['all']=pager['all']+1
        return render_template('pager.html',pager=pager,cate=cate)
    return dict(renderNav=renderNav,renderPager=renderPager)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8080)