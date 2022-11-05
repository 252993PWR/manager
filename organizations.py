from manager import *
from manager.misc import *

@app.route('/orgRegisterForm', endpoint='orgRegisterForm')
def registerForm():
    return render_template('orgRegisterForm.html')

@app.route('/orgLoginForm', endpoint='orgLoginForm')
def loginForm():
    return render_template('orgLoginForm.html')
