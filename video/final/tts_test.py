import asyncio, sys, edge_tts
async def main():
    for name,voice in [("hila","he-IL-HilaNeural"),("avri","he-IL-AvriNeural")]:
        for k,t in [("a","קוראים לו יעקב אגם. לזה קוראים פוליּמורף. היא נחנכה ב־1986."),("b","הטבעות סבבו. ארבע מאות ושמונה פאות. חנוכייה.")]:
            await edge_tts.Communicate(t, voice).save(f"clips/test_{name}_{k}.mp3")
asyncio.run(main())
