// 資料檔自我檢查：node notes/check_stops.js
const fs=require('fs');
const f=new Function(fs.readFileSync('data/stops.js','utf8')+';return {P1,P2,P3,RAIN_P1,RAIN_P2,COORDS,PREP,DAYS}');
const D=f();
const all=[...D.P1,...D.P2,...D.P3,...D.RAIN_P1,...D.RAIN_P2];
console.log('P1',D.P1.length,'P2',D.P2.length,'P3',D.P3.length,'RAIN_P1',D.RAIN_P1.length,'RAIN_P2',D.RAIN_P2.length);
console.log('missing COORDS:',all.filter(d=>!D.COORDS[d[4]]).map(d=>d[1]));
console.log('P3 times:',D.P3.map(d=>d[0]).join(' '));
console.log('RAIN_P2 times:',D.RAIN_P2.map(d=>d[0]).join(' '));
console.log('PREP',D.PREP.length,'9/16 rows',D.DAYS[1][3].length,'YOASOBI:',JSON.stringify(D).includes('YOASOBI'));
