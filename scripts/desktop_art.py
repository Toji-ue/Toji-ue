"""Original Toji desktop vector artwork. No scripts, external fonts or images."""
from html import escape
from datetime import date

C = '#48303e'
CREAM = '#fbf2ed'
MAUVE = '#b891a6'
LAV = '#c5bedc'
ORANGE = '#de946e'


def text(x,y,value,size=18,color=C,weight=400,family='sans-serif'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'


def svg(w,h,title,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{body}</svg>'


def paw(x,y,s=1):
    return f'<g transform="translate({x} {y}) scale({s})" fill="{MAUVE}"><path d="M0 9C-10 2-15 19-7 22Q0 18 7 22C15 19 10 2 0 9Z"/><ellipse cx="-11" cy="5" rx="3.2" ry="4.5" transform="rotate(-25 -11 5)"/><ellipse cx="-4" cy="0" rx="3.2" ry="4.5"/><ellipse cx="4" cy="0" rx="3.2" ry="4.5"/><ellipse cx="11" cy="5" rx="3.2" ry="4.5" transform="rotate(25 11 5)"/></g>'


def goggles(x,y,s=1):
    return f'''<g transform="translate({x} {y}) scale({s})" stroke="{C}" stroke-width="2.5" stroke-linejoin="round">
    <path d="M0 15H88" stroke="{ORANGE}" stroke-width="9"/>
    <path d="M8 3Q24-3 38 3V29H6Z M50 3Q64-2 80 3L83 29H50Z" fill="{ORANGE}"/>
    <path d="M12 7H33V23H11Z M55 7H75L77 23H55Z" fill="{LAV}" stroke-width="1.5"/>
    <path d="M38 13Q44 8 50 13" fill="none"/>
    <path d="M15 10L27 10M58 10H70" stroke="{CREAM}" stroke-width="3"/></g>'''


def window(w,h,title,subtitle='',color=LAV):
    b = f'<rect x="7" y="9" width="{w-11}" height="{h-13}" rx="7" fill="{C}"/>'
    b += f'<rect x="2" y="2" width="{w-11}" height="{h-13}" rx="5" fill="{CREAM}" stroke="{C}" stroke-width="2"/>'
    b += f'<path d="M3 38H{w-10}V7Q{w-10} 3 {w-15} 3H8Q3 3 3 8Z" fill="{color}"/>'
    b += f'<path d="M3 38H{w-10}" stroke="{C}" stroke-width="2"/>'
    b += text(18,26,title,14,C,600,'monospace')
    for i in range(3):
        x = w-79+i*21
        b += f'<rect x="{x}" y="12" width="15" height="15" fill="{CREAM}" stroke="{C}"/>'
        b += text(x+3,24,['–','□','×'][i],12,C,400,'monospace')
    if subtitle: b += text(24,69,subtitle,13,'#775c6c',400,'monospace')
    return b


def render_cards(d):
    w=720
    b=window(w,260,'01 / activity monitor','OWNED REPOSITORIES · PUBLIC + PRIVATE')
    for i,(label,val) in enumerate([('repositories',d['repositories']),('contributions / year',d['contributions']),('public stars',d['stars']),('followers',d['followers'])]):
        x=26+i*171
        b+=text(x,132,f'{val:,}',40,C,600)
        b+=text(x,160,label,12,'#775c6c',400,'monospace')
        if i<3: b+=f'<path d="M{x+150} 90V172" stroke="#dbc9d1"/>'
    b+=f'<path d="M24 192H681" stroke="#dbc9d1"/>'
    b+=text(26,222,'SYNCHRONIZED  '+d['updated'],13,'#775c6c',400,'monospace')+paw(666,215,.7)
    cards={'assets/stats.svg':svg(w,260,'Toji: repository and contribution totals',b)}
    langs=list(sorted(d['languages'].items(),key=lambda x:-x[1]))
    top=langs[:5]
    if len(langs)>5: top.append(('Other',sum(n for _,n in langs[5:])))
    total=sum(d['languages'].values())
    colors=[MAUVE,LAV,ORANGE,'#9fa790','#a6bac0','#d9c5b5']
    b=window(w,330,'02 / language palette','WHAT MY REPOSITORIES ARE MADE OF', '#dac6d0')
    x=26
    if total:
        for (name,n),col in zip(top,colors):
            width=650*n/total
            b+=f'<rect x="{x}" y="92" width="{width}" height="24" fill="{col}"/>'
            x+=width
        for i,((name,n),col) in enumerate(zip(top,colors)):
            x=26+(i%2)*335; y=155+(i//2)*42
            b+=f'<rect x="{x}" y="{y-13}" width="13" height="13" rx="3" fill="{col}" stroke="{C}"/>'
            b+=text(x+24,y,name,16)+text(x+232,y,f'{n/total:.1%}',15,C,500,'monospace')
    else: b+=text(26,150,'No language bytes reported yet.')
    b+=text(26,291,'BY BYTES · INCLUDES PRIVATE + ARCHIVED · EXCLUDES FORKS',11,'#775c6c',400,'monospace')
    cards['assets/languages.svg']=svg(w,330,'Language composition, public and private owned non-fork repositories',b)
    b=window(w,278,'03 / a year in little squares','12 MONTHS · GITHUB CONTRIBUTIONS','#d6d5bd')
    days=d['days']; offset=days[0]['weekday']
    weeks=(len(days)+offset+6)//7
    step=min(12,644/weeks); cell=step-2
    peak=max(1,max(day['count'] for day in days))
    colors=['#e8dce2','#d1b6c7','#b68ba4','#8b607c',C]
    last_month=''
    for i,day in enumerate(days):
        idx=i+offset; week=idx//7
        x=27+week*step; y=105+day['weekday']*step
        level=0 if not day['count'] else min(4,1+int(3*day['count']/peak))
        b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2" fill="{colors[level]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
        month=day['date'][:7]
        if month!=last_month and day['date'][8:]=='01':
            b+=text(x,94,date.fromisoformat(day['date']).strftime('%b'),10,'#775c6c',400,'monospace');last_month=month
    b+=text(27,214,f'{d["contributions"]:,} contributions',16,C,600)
    for i,col in enumerate(colors): b+=f'<rect x="{570+i*17}" y="202" width="12" height="12" rx="2" fill="{col}"/>'
    scope='Includes anonymized private contributions.' if d.get('private_calendar_verified') else 'Private calendar visibility pending verification.'
    b+=text(27,246,scope,12,'#775c6c',400,'monospace')
    cards['assets/activity.svg']=svg(w,278,'GitHub contribution calendar, last twelve months',b)
    cards.update(mobile_cards(d))
    return cards


def mobile_cards(d):
    w=420
    b=window(w,322,'01 / activity monitor')
    for i,(label,val) in enumerate([('repositories',d['repositories']),('contributions / year',d['contributions']),('public stars',d['stars']),('followers',d['followers'])]):
        x=24+(i%2)*195; y=94+(i//2)*98
        b+=text(x,y,f'{val:,}',36,C,600)+text(x,y+26,label,13,'#775c6c',400,'monospace')
    b+=text(24,274,'Public + private · owned · non-fork',13,'#775c6c')
    b+=text(24,296,'Updated '+d['updated'],12,'#775c6c',400,'monospace')
    cards={'assets/stats-mobile.svg':svg(w,322,'Toji repository and contribution totals',b)}
    b=window(w,388,'02 / language palette',color='#dac6d0')
    langs=sorted(d['languages'].items(),key=lambda x:-x[1]); top=langs[:5]
    if len(langs)>5: top.append(('Other',sum(n for _,n in langs[5:])))
    total=sum(d['languages'].values())
    for i,((name,n),col) in enumerate(zip(top,[MAUVE,LAV,ORANGE,'#9fa790','#a6bac0','#d9c5b5'])):
        y=80+i*43
        b+=f'<rect x="24" y="{y-13}" width="14" height="14" rx="3" fill="{col}" stroke="{C}"/>'
        b+=text(50,y,name,18)+text(315,y,f'{n/total:.1%}',16,C,500,'monospace')
    if not total: b+=text(24,80,'No language data yet.')
    b+=text(24,345,'By bytes · public + private + archived',13,'#775c6c')+text(24,368,'Forks excluded. Not a proficiency score.',12,'#775c6c')
    cards['assets/languages-mobile.svg']=svg(w,388,'Repository language composition',b)
    days=d['days']; offset=days[0]['weekday']; peak=max(1,max(x['count'] for x in days))
    b=window(w,388,'03 / a year in squares')
    colors=['#e8dce2','#d1b6c7','#b68ba4','#8b607c',C]
    for i,day in enumerate(days):
        idx=i+offset; week=idx//7; group=week//27; col=week%27
        x=24+col*13.4; y=90+group*130+day['weekday']*13.4
        level=0 if not day['count'] else min(4,1+int(3*day['count']/peak))
        b+=f'<rect x="{x:.1f}" y="{y:.1f}" width="11.4" height="11.4" rx="2" fill="{colors[level]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
    b+=text(24,73,days[0]['date']+' →',12,'#775c6c',400,'monospace')
    b+=text(24,203,'→ '+days[-1]['date'],12,'#775c6c',400,'monospace')
    b+=text(24,336,f'{d["contributions"]:,} contributions / 12 months',17,C,600)
    b+=text(24,364,'Private counts verified.' if d.get('private_calendar_verified') else 'Private visibility not yet verified.',12,'#775c6c')
    cards['assets/activity-mobile.svg']=svg(w,388,'GitHub contributions, twelve months in two rows',b)
    return cards


def static_cards():
    b=window(720,310,'toji / about.txt',color='#dac6d0')
    b+=text(28,91,'Hey, I’m Toji.',34,C,700)
    b+=text(28,125,'Student developer. Websites & small tools.',19)
    b+=text(28,158,'A sleepy raccoon is usually nearby.',17,'#775c6c')
    b+=text(28,206,'BUILDING',12,'#775c6c',600,'monospace')+text(151,206,'TypeScript · Next.js · React',17)
    b+=text(28,236,'EXPLORING',12,'#775c6c',600,'monospace')+text(151,236,'three.js · Blender',17)
    b+=text(28,266,'OFFSCREEN',12,'#775c6c',600,'monospace')+text(151,266,'Games · anime · music',17)
    b+=goggles(587,72,.85)+paw(641,203,1.2)
    cards={'assets/about.svg':svg(720,310,'About Toji: student developer, websites and small tools',b)}
    b=window(720,232,'tools / frequently opened',color='#d6d5bd')
    for i,(label,value) in enumerate([('WEB','TypeScript / Next.js / React / Tailwind'),('MOTION','GSAP / ScrollTrigger / Lenis / SVG'),('BACKEND','PostgreSQL / Prisma / Auth.js / R2'),('SHIPPING','Docker / GitHub Actions')]):
        y=79+i*39
        b+=text(27,y,label,12,'#775c6c',600,'monospace')+text(150,y,value,16)
    cards['assets/toolkit.svg']=svg(720,232,'Toji toolkit',b)
    b=window(720,205,'projects / Steam-Unblock',color='#ecc3a8')
    b+=text(27,87,'A small tool for a stubborn connection.',24,C,600)
    b+=text(27,120,'Windows utility for working around Steam access issues.',17)
    b+=text(27,154,'PowerShell core · C# / WPF interface',15,'#775c6c',400,'monospace')
    b+=paw(655,146,.8)
    cards['assets/project.svg']=svg(720,205,'Steam-Unblock Windows utility, PowerShell and C# WPF',b)
    b=window(420,370,'toji / about.txt',color='#dac6d0')
    b+=text(24,94,'Hey, I’m Toji.',32,C,700)+goggles(310,65,.75)
    b+=text(24,133,'Student developer.',20)+text(24,161,'Websites & small tools.',20)
    b+=text(24,198,'A sleepy raccoon is usually nearby.',15,'#775c6c')
    for i,(a,v) in enumerate([('BUILDING','TypeScript · Next.js · React'),('EXPLORING','three.js · Blender'),('OFFSCREEN','Games · anime · music')]):
        b+=text(24,237+i*42,a,10,'#775c6c',600,'monospace')+text(24,256+i*42,v,16)
    # Last line needs breathing room inside the window.
    cards['assets/about-mobile.svg']=svg(420,370,'About Toji',b)
    b=window(420,340,'tools / frequently opened',color='#d6d5bd')
    for i,(label,v1,v2) in enumerate([('WEB','TypeScript · Next.js · React','Tailwind CSS'),('MOTION','GSAP · ScrollTrigger · Lenis · SVG',''),('BACKEND','PostgreSQL · Prisma · Auth.js · R2',''),('SHIPPING','Docker · GitHub Actions','')]):
        y=72+i*68
        b+=text(24,y,label,11,'#775c6c',600,'monospace')+text(24,y+23,v1,16)
        if v2: b+=text(24,y+43,v2,16)
    cards['assets/toolkit-mobile.svg']=svg(420,340,'Toji toolkit',b)
    b=window(420,239,'projects / Steam-Unblock',color='#ecc3a8')
    b+=text(24,85,'A small tool for a',24,C,600)+text(24,114,'stubborn connection.',24,C,600)
    b+=text(24,153,'Working around Steam access issues',16)+text(24,177,'on Windows.',16)
    b+=text(24,209,'PowerShell · C# / WPF',15,'#775c6c',400,'monospace')
    cards['assets/project-mobile.svg']=svg(420,239,'Steam-Unblock Windows utility',b)
    return cards


if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    for name,content in static_cards().items():
        (root/name).write_text(content,encoding='utf-8')
