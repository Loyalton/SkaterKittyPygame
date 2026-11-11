/**
 * Skater Kitty - shared leaderboard (OPTIONAL).
 * A tiny Google Apps Script web app that keeps every finished run in a Google Sheet and
 * hands the top scores back to the game.  The sheet IS the "file of who has played".
 *
 * SET-UP (about 5 minutes, free):
 *   1. Go to sheets.google.com and create a new, empty spreadsheet (call it "Skater Kitty scores").
 *   2. In the sheet: Extensions > Apps Script. Delete what is there and paste this whole file. Save.
 *   3. Click Deploy > New deployment > type "Web app".
 *        Execute as: Me          Who has access: Anyone
 *      Click Deploy and allow the permissions it asks for.
 *   4. Copy the "Web app URL" (it ends in /exec).
 *   5. In main.py set   LEADERBOARD_URL = "<that URL>"   then rebuild with pygbag and push as usual.
 *
 * The sheet gets a tab called "Scores" with the columns: time | initials | score | device.
 * If you change this script later use Deploy > Manage deployments > Edit > New version
 * (otherwise the old version keeps running).
 *
 * NOTE: scores come from the player's browser, so a determined person could send fake scores.
 * This script only accepts 3-letter initials and scores from 1 to MAX_SCORE. Delete rows by hand
 * in the sheet if you ever need to.
 */
var SHEET_NAME = 'Scores';
var MAX_SCORE = 5999;

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['time', 'initials', 'score', 'device']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function top_(n) {
  var sh = sheet_();
  var last = sh.getLastRow();
  if (last < 2) return [];
  var rows = sh.getRange(2, 1, last - 1, 4).getValues();
  rows = rows.filter(function (r) { return /^[A-Z]{3}$/.test(String(r[1])) && typeof r[2] === 'number'; });
  rows.sort(function (a, b) { return b[2] - a[2]; });
  return rows.slice(0, n).map(function (r) { return { n: String(r[1]), s: r[2] }; });
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  var out;
  try {
    if (p.action === 'submit') {
      var name = String(p.name || '').toUpperCase();
      var score = parseInt(p.score, 10);
      if (/^[A-Z]{3}$/.test(name) && score >= 1 && score <= MAX_SCORE) {
        sheet_().appendRow([new Date(), name, score, String(p.id || '').substring(0, 16)]);
      }
    }
    var n = Math.max(1, Math.min(10, parseInt(p.n, 10) || 3));
    out = { top: top_(n) };
  } catch (err) {
    out = { top: [], error: String(err) };
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput(JSON.stringify(out)).setMimeType(ContentService.MimeType.JSON);
}
