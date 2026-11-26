# אנימציה: טיוטה 1 (שלב 4)

- `draft_v1.mp4`: 1920x1080, 30 fps, 118 s, בלי אודיו. `index.html`: ניגון חי עם סרגל גלילה (פתחו בדפדפן, `?t=45` קופץ לשנייה).
- `timeline.json`: **מקור יחיד** לזמני הסצנות, למעברים, לאזור הכתוביות (`subtitleZone`), ל־`subtitles` (מערך `{start,end,text}`, `\n` = שורה שנייה) ול־`narration` (נתיב קובץ שמע, ינוגן בסנכרון עם הסרגל). אחרי עריכה: `python sync_timeline.py` (כותב `timeline.js` לשימוש `index.html` מ־file://).
- רינדור: `.venv\Scripts\python render.py --video draft_v1.mp4` (Edge headless + ffmpeg מ־imageio-ffmpeg, כ־10 דקות); תמונות בדיקה: `--stills 5,60 --out stills`. גיליון: `contact.py`.
- קוד: `js/lib.js` (צורות), `js/glyphs.js` (אותיות קו־ונקודה, ג לפי לוגו המוזיאון), `js/scenes_a.js` / `scenes_b.js` (סצנות), `js/engine.js` (`seek(t)`, מעברים, כתוביות).
- כתוביות שלב 5: מלאו `subtitles` ב־`timeline.json`; הן נצבעות אוטומטית באזור התחתון (y 900 עד 1040). כל התוכן בסרטון נמצא מעל y=880.
