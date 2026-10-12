#!/usr/bin/env python3
"""Apply PG Robotics PWA editor usability v0.14 to v0.13 Flutter sources.

Run after v0.13 overlay in the GitHub Pages workflow.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def change(path, replacements):
    p=ROOT/path
    s=p.read_text(encoding='utf-8')
    for old,new in replacements:
        n=s.count(old)
        if n!=1:
            raise RuntimeError(f'{path}: expected exactly one match, got {n}: {old[:75]!r}')
        s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
    print('Updated', path)

change('lib/news_sheet.dart',[
    ("        publishNow = j['publishNow'] != false;", "        publishNow = j['publishNow'] != false,\n        sendPush = j['notify'] != false;"),
    ("  final bool publishNow;", "  final bool publishNow, sendPush;"),
    ("    'publishAt': publishAt, 'publishNow': publishNow,", "    'publishAt': publishAt, 'publishNow': publishNow, 'notify': sendPush,"),
    ("    return DraggableScrollableSheet(\n", "    return AnimatedPadding(\n      duration: const Duration(milliseconds: 210),\n      curve: Curves.easeOutCubic,\n      padding: EdgeInsets.only(bottom: MediaQuery.viewInsetsOf(context).bottom),\n      child: DraggableScrollableSheet(\n"),
    ("        ]),\n      ),\n    );\n  }\n}\n\nWidget _handle()", "        ]),\n      ),\n    ));\n  }\n}\n\nWidget _handle()"),
    ("  final _imageUrl = TextEditingController();", "  final _imageUrl = TextEditingController();\n  final _titleFocus = FocusNode();\n  final _bodyFocus = FocusNode();\n  final _titleFieldKey = GlobalKey();\n  final _bodyFieldKey = GlobalKey();"),
    ("  bool _notification = false;", "  bool _notification = true; // Push is enabled by default for every new article."),
    ("    super.initState();\n    final n = widget.existing;", "    super.initState();\n    _titleFocus.addListener(() {\n      if (_titleFocus.hasFocus) _ensureFieldVisible(_titleFieldKey);\n    });\n    _bodyFocus.addListener(() {\n      if (_bodyFocus.hasFocus) _ensureFieldVisible(_bodyFieldKey);\n    });\n    final n = widget.existing;"),
    ("      _notification = n.kind == 'notification';", "      _notification = n.sendPush;"),
    ("    _title.dispose();_body.dispose();_imageUrl.dispose();", "    _titleFocus.dispose();_bodyFocus.dispose();\n    _title.dispose();_body.dispose();_imageUrl.dispose();"),
    ("  void _message(String msg) {", "  void _ensureFieldVisible(GlobalKey key) {\n    // Safari's keyboard has a slide-in animation: scroll after it settles.\n    Future<void>.delayed(const Duration(milliseconds: 330), () {\n      if (!mounted || key.currentContext == null) return;\n      Scrollable.ensureVisible(key.currentContext!,\n        duration: const Duration(milliseconds: 250),\n        curve: Curves.easeOutCubic,\n        alignment: .18,\n      );\n    });\n  }\n\n  void _message(String msg) {"),
    ("      'kind': _notification ? 'notification' : 'news',", "      'kind': widget.existing?.kind ?? 'news',"),
    ("      'tagUa': _notification ? 'СПОВІЩЕННЯ' : 'НОВИНА',", "      'tagUa': widget.existing?.tagUa ?? 'НОВИНА',"),
    ("      'tagEn': _notification ? 'NOTICE' : 'NEWS',", "      'tagEn': widget.existing?.tagEn ?? 'NEWS',"),
    ("      'publishNow': _publishNow,", "      'notify': _notification,\n      'publishNow': _publishNow,"),
    ("        TextField(controller: _imageUrl, onChanged: (_) => setState(() {\n          _imageBase64 = ''; _dirty = true;\n        }),\n          decoration: InputDecoration(labelText: ua ? 'Або URL фотографії' : 'Or image URL',\n            helperText: ua ? 'Для ручного кадрування оберіть фото з галереї'\n              : 'Choose gallery image to crop manually',\n            border: const OutlineInputBorder())),\n", ""),
    ("        TextField(controller: _title,maxLength: 100,", "        TextField(key: _titleFieldKey, controller: _title, focusNode: _titleFocus,\n          maxLength: 100, scrollPadding: const EdgeInsets.only(bottom: 170),\n          textInputAction: TextInputAction.next,\n          onSubmitted: (_) => _bodyFocus.requestFocus(),"),
    ("        TextField(controller: _body,maxLines: 6,minLines: 3,maxLength: 3000,", "        TextField(key: _bodyFieldKey, controller: _body, focusNode: _bodyFocus,\n          maxLines: 6,minLines: 3,maxLength: 3000,\n          scrollPadding: const EdgeInsets.only(bottom: 200),\n          keyboardType: TextInputType.multiline,"),
])
change('lib/pg_backend.dart',[
    ("      'kind':item['kind'], 'title':item['titleUa'], 'body':item['bodyUa'],", "      'kind':item['kind'], 'title':item['titleUa'], 'body':item['bodyUa'],\n      'notify':item['notify'] != false,"),
])
change('pubspec.yaml',[
    ('version: 0.13.0+13','version: 0.14.0+14'),
])
print('Validated v0.14 source patch successfully')