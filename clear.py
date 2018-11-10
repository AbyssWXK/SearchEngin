import hello
all_music = hello.Music.query.all()
UselessId=[]
i=0
for music in all_music:
    i=i+1
    aft_musiclist= all_music[i:]
    for aft_music in aft_musiclist:
        if music.musicname==aft_music.musicname:
            UselessId.append(aft_music.id)
for music in all_music:
    if music.em1==0 and music.em2==0 and music.em3==0 and music.em4==0 and music.em5==0 and \
            music.em6==0 and music.em7==0 and music.em8==0 and music.em9==0 and music.em10==0 :
        UselessId.append(music.id)

new_useless=[]
for id in UselessId:
    if id not in new_useless:
        new_useless.append(id)
print(new_useless)
for mid in new_useless:
    useless = hello.Music.query.filter_by(id=mid).first()
    print(useless)
    hello.db.session.delete(useless)
    hello.db.session.commit()