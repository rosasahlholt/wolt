from bottle import default_app, get, post, request, response, run, template, static_file, redirect
from icecream import ic
import os
import x
import uuid


##############################
@get("/mixhtml.js")
def _():
    return static_file("mixhtml.js", root="js")

##############################
@get("/mojocss.js")
def _():
    return static_file("mojocss.js", root="js")

##############################
@get("/mixhtml.css")
def _():
    return static_file("mixhtml.css", root="css")

##############################
@get("/logo.jpg")
def _():
    return static_file("logo.jpg", root="images")


##############################
@get("/")
def _():
    user = request.get_cookie("user", secret=x.COOKIE_SECRET)
    # if not user:
    #     print("Not logged in")
    return template("index", user=user)


##############################
@get("/login")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        if user:
            response.status = 303
            response.set_header("location", "/admin")
            return
        return template("login.html", user=user)
    except Exception as ex:
        print(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/profile")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)          
        if user is None or user.get("role", "") != "partner": # not a valid cookie. Someone tempered with it
            response.status = 303
            response.set_header("location", "/login")
            return           
        return template("profile.html", user_name=user["name"], user=user)
    except Exception as ex:
        print(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/admin")
def _():
    try:
        x.disable_cache()
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        if user is None: # not a valid cookie. Someone tempered with it
            response.status = 303
            response.set_header("location", "/login")
            return   
        db = x.db()
        q = db.execute("SELECT * FROM users")
        users = q.fetchall()            
        return template("admin.html", user_name=user["user_name"], user=user, users=users)
    except Exception as ex:
        print(ex)
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()

##############################
@get("/signup")
def _():
    try:
        user = request.get_cookie("user", secret=x.COOKIE_SECRET)
        return template("signup.html", user=user)
    except Exception as ex:
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        pass


##############################
@get("/logout")
def _():
    response.delete_cookie("user")
    return redirect("/login")


##############################
@post("/login")
def _():
    try:

        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db = x.db()
        q = db.execute("""
                        SELECT user_pk, user_name, user_last_name, user_email FROM users 
                        WHERE user_email = ? AND 
                        user_password=? LIMIT 1
                       """,(user_email, user_password))
        user = q.fetchall()
        if not user:
            toast = template("__toast", message="Invalid credentials")
            return toast
        response.set_cookie("user", user[0], secret=x.COOKIE_SECRET)
        return "<template mix-redirect='/admin'></template>"
        print(user)
        db.commit()
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()


##############################
@post("/signup")
def _():
    try:
        user = {
            "user_pk": str(uuid.uuid4()),
            "user_username": x.validate_user_username(),
            "user_name" : x.validate_user_name(),
            "user_last_name" : x.validate_user_last_name(),
            "user_email" : x.validate_user_email(),
            "user_password" : x.validate_user_password()
        }

        db = x.db()
        # binding variables by value, # bind parameters
        q = db.execute("INSERT INTO users VALUES(:user_pk, :user_username, :user_name, :user_last_name, :user_email,:user_password)", user)

        # q = db.execute("INSERT INTO users VALUES(?,?,?,?,?)",(
        #     user_pk, user_name, user_last_name, user_email, user_password
        # ))
        db.commit()
        # toast = template("__toast.html", message="SUCCESS")
        return "<template mix-redirect='/login'></template>"
    except Exception as ex:
        print(ex)
        if "db" in locals(): db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]            
            toast = template("__toast.html", message=ex.args[0])
            return toast
        else: # python exception, not under our control. The exception will always have an error message in ex.args[0]
            if "users.user_email" in ex.args[0]: # UNIQUE constraint failed: users.user_email
                response.status = 409 # conflict
                toast = template("__toast", message="Email not available")
                return toast    
            if "users.user_username" in ex.args[0]: # UNIQUE constraint failed: users.user_email
                response.status = 409 # conflict
                toast = template("__toast", message="Username not available")
                return toast                          
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()


##############################
@get("/transaction")
def _():
    try:
        db = x.db()
        q = db.execute("INSERT INTO users VALUES(?,?)",("1","A"))
        db.commit()
    except Exception as ex:
        db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()

##############################
@get("/users/delete/<user_pk>")
def _(user_pk):
    try:
        # TODO: Validate the uuid4
        # db = x.db()
        # q = db.execute("",())
        # db.commit()
        return f"<template mix-target='#u{user_pk}'></template>"
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()

##############################
@get("/users/block/<user_pk>")
def _(user_pk):
    try:
        # TODO: validate user_pk
        # db = x.db()
        # q = db.execute("",())
        # db.commit()
        btn_unblock = template("___unblock.html")
        toast = template("__toast.html", message="User blocked")
        return f"""
                <template 
                mix-target='#block-{user_pk}' 
                mix-replace>
                    {btn_unblock}
                </template>
                <template mix-target="body" mix-top>
                    {toast}
                </template>
                """
    except Exception as ex:
        print(ex)
        if "db" in locals():db.rollback()
        if len(ex.args) >= 2: # own created exception
            response.status = ex.args[1]
            return {"error":ex.args[0]}
        else: # python exception, not under our control
            error = "System under maintenance. Please try again"
            response.status = 500
            return {"error":f"{error}"}
    finally:
        if "db" in locals(): db.close()







application = default_app()
##############################
# if "PYTHONANYWHERE_DOMAIN" in os.environ:
#     application = default_app()
# else:
#     ic("Server listening...")
#     run(host="0.0.0.0", port=80, debug=True, reloader=True, interval=0.5)

##############################

