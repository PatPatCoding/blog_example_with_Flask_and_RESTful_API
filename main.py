from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime as dt

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # def to_dict(self):
    #     return {column.name: getattr(self, column.name) for column in self.__table__.columns}


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    # body = StringField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    # posts = db.session.query(BlogPost).all()
    # requested_post = None
    # for blog_post in posts:
    #     if blog_post.id == index:
    #         requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/add", methods=('GET', 'POST'))
def new_post():
    form = CreatePostForm()
    today = dt.now().strftime("%B %d, %Y")
    if form.validate_on_submit():
        added_post = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            date=today,
            body=request.form['body'],
            author=request.form['author'],
            img_url=request.form['img_url'])
        db.session.add(added_post)
        db.session.commit()
        # with open('cafe-data.csv', 'a', encoding="utf8") as csv_file:
        #     csv_file.write(f"\n{form.cafe.data},{form.location.data},{form.open.data},{form.close.data},{form.coffee.data},{form.wifi.data},{form.power.data}")
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/edit-post/<int:post_id>", methods=('GET', 'POST'))
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    form = CreatePostForm(title=post.title,
                          subtitle=post.subtitle,
                          img_url=post.img_url,
                          author=post.author,
                          body=post.body)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.author = form.author.data
        post.body = form.body.data
        db.session.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, id=post_id)

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
