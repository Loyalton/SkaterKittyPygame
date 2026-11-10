# Build and deploy

1. Put these files in your repo folder (replace main.py, graphics/, audio/, version.txt, README.md, .gitignore).
2. Delete the old, unused files from the repo:
   - build/web/final_project_vmr_skater_pygamev2_pygbag.apk  (90 MB, the game never loads it)
   - build/web-cache/  (pygbag scratch folder, ~28 MB)
   - audio/ollie.ogg, audio/ollieplusRolling.ogg, audio/rollinglong5x.ogg  (already left out of this package)
3. In the project folder run:   pip install --upgrade pygbag pygame-ce
   - Test locally:              pygbag .          then open http://localhost:8000
   - Build for the web:         pygbag --build .
4. Commit and push build/web/ (index.html, favicon.png, skaterkittypygame.apk) to GitHub Pages.
5. Replace the link on your Shopify games page with embed_snippet.html.
6. Test on a real phone in landscape. Clear the browser cache once so the old .apk isn't reused.

You can still run the game on a computer with plain `python main.py` (needs pygame-ce).
