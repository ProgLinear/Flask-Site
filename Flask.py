from flask import Flask, render_template,redirect, flash, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

# USER LOGIN DECORATORS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logined_in" in session:
            return f(*args, **kwargs)
        else:
            flash("....","danger")
            return redirect(url_for("login"))
            
    
    return decorated_function

#User register | login form
class RegisterForm(Form):
    name = StringField("Ad Soyad", validators=[ validators.InputRequired(message="Ad və Soyad yazın!") ,validators.Length(min = 4,max = 20)])
    username = StringField("İstifadəçi Adı", validators=[ validators.InputRequired("İstifadəçi adı yazın!") ,validators.Length(min=4,max=20)])
    email = StringField("Email Adresi", validators=[validators.Length(min = 10, max = 40)])
    password = PasswordField("Şifrə", validators=[
         validators.InputRequired("Şifrə yazın!") ,
        validators.DataRequired(message  = "Xahiş edirik bir şifrə yazın"),
        validators.EqualTo(fieldname = "confirm", message = "Şifrə uyğun deyil")
    ])

    confirm = PasswordField( "Şifrə doğrula",validators=[validators.InputRequired("Şifrənizi doğrulayın!")])
class LoginForm(Form):
    username = StringField("İstifadəçi adı")
    password = PasswordField("Şifrə")




#$$$$$$$$$$$$$$$$$$-SQL-$$$$$$$$$$$$$$$$$$$$$$$#
app = Flask(__name__)
app.secret_key="hack"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "prog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"


mysql = MySQL(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/error1.html")


#$$$$$$$$$$$$$$$$->->->-ARTICLE CODES-<-<-<-$$$$$$$$$$$$$$$$#
# Article Form
class ArticleForm(Form):
    title = StringField("Məqalə başlığı", validators=[validators.InputRequired(message="Məqalə başlığı daxil edin!"),validators.Length(min=3,max=50)])
    content = TextAreaField("Məqalə məzmunu",validators=[validators.InputRequired(message="Məqalə məzmunu daxil edin!"), validators.Length(min=20,max=100000)])

@app.route("/addarticle", methods =  ["GET","POST"])
def addarticle():


    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()

        cursor.close()

        flash("Məqalə Uğurla əlavə edildi","success")

        return redirect(url_for("dashboard"))

    return render_template("addarticle.html",form = form)

@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)

    else:
        return render_template("articles.html")


    return "Article Id:" + id

@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where id = %s"

        cursor.execute(sorgu2,(id,))

        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("belə bir məqalə yoxdur vəya buna səlahiyyativiz yoxdur!","danger")
        return redirect(url_for("index"))

@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
   if request.method == "GET":
       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where id = %s and author = %s"
       result = cursor.execute(sorgu,(id,session["username"]))

       if result == 0:
           flash("belə bir məqalə yoxdur vəya buna səlahiyyativiz yoxdur!","danger")
           return redirect(url_for("index"))
       else:
           article = cursor.fetchone()
           form = ArticleForm()

           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)

   else:
       # POST REQUEST
       form = ArticleForm(request.form)

       newTitle = form.title.data
       newContent = form.content.data

       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "

       cursor = mysql.connection.cursor()

       cursor.execute(sorgu2,(newTitle,newContent,id))

       mysql.connection.commit()

       flash("Məqalə uğurla əlavə olundu!","success")

       return redirect(url_for("dashboard"))

       pass


@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
        return render_template("dashboard.html")

@app.route("/ADMIN_SITE_DASHBOARD")
@login_required
def dash():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
        return render_template("dashboard.html")

@app.route("/search",methods =["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))

    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where title like '%" + keyword +"%'"
        result = cursor.execute(sorgu)

        if result == 0:
            flash("Axtarış uğursuz başa çatdı","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()
            return render_template("articles.html",articles = articles)


#$$$$$$$$$$$$$$$$->->->-USER CODES-<-<-<-$$$$$$$$$$$$$$$$#
@app.route("/register", methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password =  sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()


        cursor.close()
        flash("Qeydiyyatınız uğurlu alındı","success")

        return redirect(url_for("login"))


    else:
        return render_template("register.html", form = form)

@app.route("/login", methods = ["GET","POST"])
def login():

    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "Select * From users where username = %s"
        result = cursor.execute(sorgu,(username,))
        

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Uğurla Daxil oldunuz","success")

                session["logined_in"] = True
                session["username"] = username


                return redirect(url_for("index"))

            else:
                flash("şifrə yanlışdır!","danger")
                return redirect(url_for("login"))

        

        

        else:  
            flash("Belə bir istifadəçi yoxdur","danger")
            return redirect(url_for("login"))

    
    return render_template("login.html", form = form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))




if __name__ == "__main__":
    app.run(debug=True)  













#explanations
    # @app.route("")<--/# | Web-page url structure
    # @login_required | əgər bu olmasa login lazim olmaz
    # render_templaate("")<--index.html | html page insert python
 
    # {% extends "layout.html" %} | indexin icine layout eklemek
    # {% include "includes/navbar.html" %} | layout-un içinə include(parça) elave etmək
    
    # methods = ["GET","POST"]
    
 