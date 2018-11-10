# -- coding: utf-8 --
import os
import tools
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from classifiers import DictClassifier



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'mysql://root:112358@localhost/music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

class IdSim():
    def __init__(self, mid, sim):
        self.mid = mid
        self.sim = sim
    def __repr__(self):
        return '%d %.2f' % (self.mid, self.sim)

class Music(db.Model):
    __tablename__ = 'musiclist'
    id = db.Column(db.Integer, primary_key=True)
    musicname = db.Column(db.VARCHAR(45))
    em1 = db.Column(db.Float)
    em2 = db.Column(db.Float)
    em3 = db.Column(db.Float)
    em4 = db.Column(db.Float)
    em5 = db.Column(db.Float)
    em6 = db.Column(db.Float)
    em7 = db.Column(db.Float)
    em8 = db.Column(db.Float)
    em9 = db.Column(db.Float)
    em10 = db.Column(db.Float)
    major = db.Column(db.Integer)
    def __init__(self, musicname, em1, em2, em3, em4, em5, em6, em7, em8, em9, em10):
        self.id = None
        self.musicname = musicname
        self.em1 = em1
        self.em2 = em2
        self.em3 = em3
        self.em4 = em4
        self.em5 = em5
        self.em6 = em6
        self.em7 = em7
        self.em8 = em8
        self.em9 = em9
        self.em10 = em10
        self.major = tools.Maxid([em1, em2, em3, em4, em5, em6, em7, em8, em9, em10])
    def __repr__(self):
        return '<Music %s %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f>' %  \
               (self.musicname, self.em1, self.em2, self.em3, self.em4, self.em5, self.em6, self.em7, self.em8, self.em9, self.em10)
    def save_db(self):
        db.session.add(self)
        db.session.commit()

class KeywordForm(FlaskForm):
    Keyword = StringField('Emotional Sentences', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = KeywordForm()
    if form.validate_on_submit():
        keyword = form.Keyword.data
        return redirect(url_for('mlist', keyword = keyword))
    return render_template('index.html', form = form)
@app.route('/result?Keyword=<keyword>')
def mlist(keyword):
    result = createlist(keyword)
    musicifo= []
    for music in result:
        musicifo.append(Music.query.get(music.mid))
    return render_template('Mlist.html', result = result, musicifo = musicifo,llen = len(result), keyword = keyword)


def createlist(keyword):
    em = analysis(keyword)
    mlist = similar(em)
    return mlist
def analysis(keyword):
    # emotion analysis
    # ma = Music('keyword', 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
    d= DictClassifier()
    m = d.analyse_sentence(keyword)
    ma = Music('keyword',m['scoreai'],m['scoree'],m['scorehao'],m['scorejing'],m['scoreju'],m['scorele'],m['scorenu'],0,0,0)
    return ma

def similar(em):
    ## list sort
    vec1 = veclize(em)
    major = tools.Maxid(vec1)
    simlist = []
    slec_music = Music.query.filter_by(major=major).all()
    for vec2 in slec_music:
        simlist.append(IdSim(vec2.id, tools.Tonimoto(vec1, veclize(vec2))))    # tonimoto系数
        # simlist.append(IdSim(vec2.id, tools.Cosine(vec1, veclize(vec2)))) # 余弦度量
    simlist.sort(key = lambda x: x.sim, reverse = True)
    return simlist
def veclize(em):
    return [em.em1, em.em2,em.em3,em.em4,em.em5,em.em6,em.em7,em.em8,em.em9,em.em10]
