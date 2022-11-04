from manager import *

@app.route('/')
def mainPage():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
