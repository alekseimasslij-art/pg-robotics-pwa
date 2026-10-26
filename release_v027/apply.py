from pathlib import Path

p=Path('lib/mission_game.dart');s=p.read_text()
def rep(old,new):
 global s
 assert s.count(old)==1,(old[:90],s.count(old))
 s=s.replace(old,new)
rep('bool get canFire => kind == 1 || kind == 2 || kind == 3 ||\n      kind == 5 || (kind == 6 && phase < .45);','bool get canFire => true;')
rep('_targets.any((e) => e.kind == 5) || _targets.length >= 7','_targets.any((e) => e.kind == 5) || _targets.length >= 9')
rep('math.max(1.8, 2.9 - _wave * .045)','math.max(1.28, 2.35 - _wave * .052)')
rep('if (target.canFire && target.y > .05 && target.shotClock <= 0 &&\n          _shots.length < 16)','if (target.canFire && target.y > .05 && target.shotClock <= 0 &&\n          _shots.length < 28)')
rep('final base = switch(target.kind) {5 => 2.8, 3 => 4.8,\n          2 => 5.0, 1 => 6.6, 6 => 8.2, _ => 10.0};\n        target.shotClock = math.max(2.2, base - math.min(_wave * .13, 1.1)) +\n            _random.nextDouble() * 1.9;',
'''final base = switch(target.kind) {5 => 1.95, 3 => 2.8,
          2 => 2.9, 1 => 3.6, 6 => 4.2, _ => 5.6};
        target.shotClock = math.max(1.35, base - math.min(_wave*.09, .95)) +
            _random.nextDouble() * .8;''')
rep('final volleys=target.kind==5?3:1;',
    'final volleys=target.kind==5 ? math.min(6,3+target.tier) :\n            target.kind==2 ? 3 : target.kind==3 ? 2 : 1;')
rep('final offset=(n-(volleys-1)/2)*.20;','final offset=(n-(volleys-1)/2)*.145;')
rep('_takeDamage(14);','_takeDamage(11);')

st=s.index('  @override\n  Widget build(BuildContext context) {',s.index('class _MissionGameViewState'))
ed=s.index('\n}\n\nclass _BomberPainter',st)
new='''  Widget _hudTag(String v,{Color color=Palette.foreground})=>
    Padding(padding:const EdgeInsets.only(right:10,top:4),child:Text(v,
      maxLines:1,overflow:TextOverflow.ellipsis,style:TextStyle(
        fontSize:10,fontWeight:FontWeight.w800,color:color)));

  @override
  Widget build(BuildContext context) {
    final ua=widget.ukrainian;
    return Material(color:Palette.background,child:Stack(fit:StackFit.expand,children:[
      Positioned.fill(child:LayoutBuilder(builder:(context,box){
        final size=Size(box.maxWidth,box.maxHeight);
        return GestureDetector(behavior:HitTestBehavior.opaque,
          onPanDown:(e)=>_move(e.localPosition,size),
          onPanUpdate:(e)=>_move(e.localPosition,size),
          onTapDown:(e)=>_move(e.localPosition,size),
          child:Stack(fit:StackFit.expand,children:[
            AnimatedBuilder(animation:_frame,builder:(_,__)=>CustomPaint(
              painter:_BomberPainter(targets:_targets,world:_world,wrecks:_wrecks,
                shots:_shots,charges:_charges,pickups:_pickups,rings:_rings,
                player:Offset(_playerX,_playerY),model:_model,time:_time,
                shield:_shield>0,invulnerable:_invuln>0,
                range:_targetRange,blast:_blastRadius,target:_nearestTarget()))),
            if(_damageFlash>0)Positioned.fill(child:IgnorePointer(
              child:CustomPaint(painter:_SideHitGlow(_damageFlash/.32)))),
            if(_playing&&_time<_flashUntil)Positioned(
              top:MediaQuery.paddingOf(context).top+139,left:24,right:24,
              child:IgnorePointer(child:Center(child:Container(
                padding:const EdgeInsets.symmetric(horizontal:13,vertical:8),
                decoration:BoxDecoration(color:const Color(0xE1121719),
                  borderRadius:BorderRadius.circular(10)),
                child:Text(_flash,textAlign:TextAlign.center,style:
                  const TextStyle(color:Palette.primary,fontSize:11,
                    fontWeight:FontWeight.w900))))),
            if(!_playing)Positioned.fill(child:ColoredBox(
              color:const Color(0xDD101517),child:Center(child:Column(
                mainAxisSize:MainAxisSize.min,children:[
                  Icon(_finished?CupertinoIcons.refresh_circled:
                    CupertinoIcons.pause_circle,color:Palette.primary,size:52),
                  const SizedBox(height:12),
                  Text(_finished?(ua?'ГРУ ЗАВЕРШЕНО':'GAME OVER'):
                    (ua?'ПАУЗА':'PAUSE'),style:const TextStyle(fontSize:24,
                      fontWeight:FontWeight.w900)),
                  const SizedBox(height:12),
                  Text('${ua?'Результат':'Score'}: $_score',style:
                    const TextStyle(color:Palette.secondary,fontSize:12)),
                  const SizedBox(height:20),
                  YellowAction(title:_finished?(ua?'Заново':'Restart'):
                    (ua?'Продовжити':'Resume'),icon:CupertinoIcons.play_fill,
                    onTap:()=>_start(reset:_finished)),
                  const SizedBox(height:10),
                  TextButton.icon(onPressed:(){_pause();Navigator.of(context).maybePop();},
                    icon:const Icon(CupertinoIcons.arrow_left),
                    label:Text(ua?'До меню':'Back to menu'),
                    style:TextButton.styleFrom(foregroundColor:Colors.white)),
                ])))),
          ]));
      })),
      // Top HUD lives OVER the playfield rather than outside its viewport.
      Positioned(top:0,left:0,right:0,child:SafeArea(top:true,bottom:false,
        child:AnimatedBuilder(animation:_frame,builder:(_,__)=>Container(
          padding:const EdgeInsets.fromLTRB(8,5,8,10),
          decoration:const BoxDecoration(color:Color(0xE914181A),
            border:Border(bottom:BorderSide(color:Color(0x665D6868)))),
          child:Column(mainAxisSize:MainAxisSize.min,children:[
            Row(children:[
              SizedBox(width:42,height:42,child:IconButton(
                tooltip:ua?'До меню':'Back to menu',padding:EdgeInsets.zero,
                onPressed:(){_pause();Navigator.of(context).maybePop();},
                icon:const Icon(CupertinoIcons.arrow_left,size:24,
                  color:Palette.primary))),
              Expanded(child:Column(crossAxisAlignment:CrossAxisAlignment.start,
                children:[
                  const Text('BOMBER',style:TextStyle(fontSize:14,
                    fontWeight:FontWeight.w900,letterSpacing:1)),
                  Text(_modelName,maxLines:1,overflow:TextOverflow.ellipsis,
                    style:const TextStyle(fontSize:9,color:Palette.secondary)),
              ])),
              Column(crossAxisAlignment:CrossAxisAlignment.end,children:[
                Text('${ua?'РАХУНОК':'SCORE'} $_score',style:const TextStyle(
                  fontSize:12,fontWeight:FontWeight.w900,color:Palette.primary)),
                Text('${ua?'РЕКОРД':'BEST'} $_best',style:const TextStyle(
                  fontSize:9,color:Palette.secondary)),
              ]),
              const SizedBox(width:7),
              SizedBox(width:42,height:42,child:IconButton(
                padding:EdgeInsets.zero,
                tooltip:_playing?(ua?'Пауза':'Pause'):(ua?'Продовжити':'Resume'),
                onPressed:_playing?_pause:()=>_start(reset:_finished),
                icon:Icon(_playing?CupertinoIcons.pause_fill:
                  CupertinoIcons.play_fill,color:Palette.primary,size:23))),
            ]),
            const SizedBox(height:4),
            Row(children:[
              Text('♥ $_lives',style:const TextStyle(color:Color(0xFFFF7484),
                fontSize:13,fontWeight:FontWeight.w900)),
              const SizedBox(width:9),
              Text('HP ${_hp.ceil()}',style:const TextStyle(fontSize:10,
                fontWeight:FontWeight.w800)),
              const SizedBox(width:5),
              Expanded(child:ClipRRect(borderRadius:BorderRadius.circular(4),
                child:LinearProgressIndicator(value:(_hp/100).clamp(0.0,1.0),
                  minHeight:6,backgroundColor:Palette.border,
                  valueColor:AlwaysStoppedAnimation<Color>(_hp>35?
                    const Color(0xFF6FE5B5):const Color(0xFFFF5969))))),
              const SizedBox(width:8),
              Text('${ua?'ХВИЛЯ':'WAVE'} $_wave',style:
                const TextStyle(fontSize:10,fontWeight:FontWeight.w800)),
              const SizedBox(width:8),
              Text('${ua?'ЦІЛІ':'KILLS'} $_kills',style:
                const TextStyle(fontSize:10,fontWeight:FontWeight.w800)),
            ]),
            if(_shield>0||_boost>0||_rangeBuff>0||_multiBuff>0||_enhanced>0)
              Wrap(alignment:WrapAlignment.start,spacing:3,children:[
                if(_shield>0)_hudTag('${ua?'ЩИТ':'SHIELD'} ${_shield.ceil()}c',
                  color:const Color(0xFF66E9D7)),
                if(_boost>0)_hudTag('${ua?'ЗАРЯД':'BOOST'} ${_boost.ceil()}c',
                  color:Palette.primary),
                if(_rangeBuff>0)_hudTag('R+ ${_rangeBuff.ceil()}c',color:Palette.primary),
                if(_multiBuff>0)_hudTag('×$_maxSalvo ${_multiBuff.ceil()}c',color:Palette.primary),
                if(_enhanced>0)_hudTag('${ua?'ПОСИЛЕНА':'ENHANCED'} ${_enhanced.ceil()}c',color:Palette.primary),
              ]),
          ]))))),
      // Separate touch surface: pressing does not teleport the drone.
      Positioned(bottom:0,left:0,right:0,child:SafeArea(top:false,bottom:true,
        child:Center(child:Padding(padding:const EdgeInsets.only(bottom:10,top:5),
          child:SizedBox(width:218,height:52,child:OutlinedButton(
            onPressed:_activateUltimate,style:OutlinedButton.styleFrom(
              foregroundColor:_ultimate>=1?Palette.background:Palette.primary,
              backgroundColor:_ultimate>=1?Palette.primary:const Color(0xEE24282B),
              side:const BorderSide(color:Palette.primary,width:1.1),
              shape:RoundedRectangleBorder(borderRadius:BorderRadius.circular(14))),
            child:Column(mainAxisAlignment:MainAxisAlignment.center,children:[
              Text(_enhanced>0?'${ua?'ПОСИЛЕНА':'ENHANCED'} ${_enhanced.ceil()}c':
                _ultimate>=1?(ua?'ПОСИЛЕНА · УВІМКНУТИ':'ENHANCED · ACTIVATE'):
                '${ua?'ПОСИЛЕНА':'ENHANCED'} ${(_ultimate*100).floor()}%',
                style:const TextStyle(fontSize:11,fontWeight:FontWeight.w900)),
              const SizedBox(height:4),
              SizedBox(width:160,height:4,child:LinearProgressIndicator(
                value:_ultimate,backgroundColor:Palette.border,
                valueColor:AlwaysStoppedAnimation<Color>(
                  _ultimate>=1?Palette.background:Palette.primary))),
            ]))))))),
    ]));
  }
'''
s=s[:st]+new+s[ed:]

# Replace generic crater shape with different silhouettes based on target kind.
painter=s.index('class _BomberPainter')
st=s.index('    for(final w in wrecks){',painter)
ed=s.index('    final unit',st)
s=s[:st]+'''    for(final w in wrecks){
      _drawWreck(canvas,Offset(w.x*size.width,w.y*size.height),w.kind);
    }
'''+s[ed:]
marker='  void _label(Canvas canvas, String text, Offset center, double size,'
assert s.count(marker)==1
method='''  void _drawWreck(Canvas canvas,Offset p,int kind){
    canvas.save();canvas.translate(p.dx,p.dy);
    canvas.rotate(math.sin(p.dx*.05+kind)*.18);
    final boss=kind==5;
    final w=boss?56.0:kind==2?39.0:kind==6?27.0:33.0;
    final h=boss?63.0:kind==2?44.0:kind==4?39.0:35.0;
    canvas.drawOval(Rect.fromCenter(center:const Offset(2,3),
      width:w*1.45,height:h*.95),Paint()..color=const Color(0x98312620));
    final metal=Paint()..color=const Color(0xFF52514C);
    final dark=Paint()..color=const Color(0xFF1A1D1C);
    final edge=Paint()..color=const Color(0xFF9A826B)
      ..style=PaintingStyle.stroke..strokeWidth=1.5;
    if(kind==2||kind==5){
      // Tanks/bosses leave broken tracks, a rotated turret and cannon.
      for(final side in [-1.0,1.0]){
        canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(
          center:Offset(side*w*.52,0),width:8,height:h),
          const Radius.circular(3)),dark);
        for(var i=-2;i<=2;i++){
          final y=i*h/6;
          canvas.drawLine(Offset(side*w*.52-4,y),
            Offset(side*w*.52+4,y+1),edge);
        }
      }
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(
        center:Offset.zero,width:w*.82,height:h*.67),
        const Radius.circular(4)),metal);
      canvas.drawCircle(const Offset(7,-5),w*.20,dark);
      canvas.drawLine(const Offset(7,-5),Offset(w*.48,-h*.46),
        Paint()..color=const Color(0xFF252727)..strokeWidth=4);
      canvas.drawLine(const Offset(-11,1),const Offset(10,14),edge);
    }else if(kind==3){
      // Turret wreck: circular ring and detached gun barrel.
      canvas.drawCircle(Offset.zero,18,dark);
      canvas.drawArc(Rect.fromCircle(center:Offset.zero,radius:14),
        -.4,3.4,false,edge..strokeWidth=3);
      canvas.drawLine(const Offset(-9,6),const Offset(22,-16),
        Paint()..color=const Color(0xFF8C8170)..strokeWidth=5);
    }else{
      // APC, scout and truck: ruined hull, wheel pairs, detached panels.
      for(final sign in [-1.0,1.0]){
        for(final y in [-h*.28,h*.28]){
          canvas.drawCircle(Offset(sign*w*.48,y),4.5,dark);
          canvas.drawCircle(Offset(sign*w*.48,y),2,
            Paint()..color=const Color(0xFF9B917C));
        }
      }
      final hull=Path()..moveTo(-w*.40,-h*.46)
        ..lineTo(w*.32,-h*.37)..lineTo(w*.45,h*.23)
        ..lineTo(w*.16,h*.43)..lineTo(-w*.39,h*.27)..close();
      canvas.drawPath(hull,metal);canvas.drawPath(hull,edge);
      canvas.drawLine(Offset(-w*.3,-h*.2),Offset(w*.25,h*.3),
        Paint()..color=const Color(0xFF171B1B)..strokeWidth=3);
      if(kind==4){
        canvas.drawRRect(RRect.fromRectAndRadius(
          const Rect.fromLTWH(-10,-14,20,11),const Radius.circular(2)),
          Paint()..color=const Color(0xFF868477));
      }else if(kind==1){
        canvas.drawRRect(RRect.fromRectAndRadius(
          const Rect.fromLTWH(-9,-14,16,17),const Radius.circular(2)),dark);
      }else{
        canvas.drawLine(const Offset(-9,-9),const Offset(13,-17),
          Paint()..color=const Color(0xFF97886C)..strokeWidth=3);
      }
    }
    for(var i=0;i<6;i++){
      final angle=i*1.13+kind*.71,dist=math.min(w*.7,10+i*2.0);
      final dx=math.cos(angle)*dist,dy=math.sin(angle)*dist*.58;
      canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromCenter(
        center:Offset(dx,dy),width:2.5+(i%3)*1.4,height:3+(i%2)*2),
        const Radius.circular(.7)),Paint()..color=i.isEven?
        const Color(0xFF8D7D68):const Color(0xFF2B2C29));
    }
    canvas.restore();
  }

'''
s=s.replace(marker,method+marker)
p.write_text(s)

p=Path('deploy/pg_model_viewer.html');html=p.read_text()
assert html.count("eye.textContent='👁';")==2
html=html.replace("eye.textContent='👁';",'eye.innerHTML=eyeSvg(specsCollapsed);')
needle="  const eye=document.createElement('button');eye.type='button';"
assert html.count(needle)==1
svg='''  const eyeSvg=(hidden)=>'<svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="#ffde19" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><path d="M2 12s3.5-6.5 10-6.5S22 12 22 12s-3.5 6.5-10 6.5S2 12 2 12Z"/><circle cx="12" cy="12" r="2.7"/>'+(hidden?'<path d="M3 21 21 3" stroke-width="2.2"/>':'')+'</svg>';
'''
html=html.replace(needle,svg+needle)
html=html.replace('#specs button{border:1px solid #777',
    '#specs button{display:flex;align-items:center;justify-content:center;border:1px solid #777')
p.write_text(html)

p=Path('pubspec.yaml');text=p.read_text()
assert 'version: 0.26.0+26' in text
p.write_text(text.replace('version: 0.26.0+26','version: 0.27.0+27'))
print('v0.27 patch applied')