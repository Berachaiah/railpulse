(() => {

const canvas = document.getElementById("shader-canvas");

if (!canvas) return;

const ctx = canvas.getContext("2d");

function resize() {
    canvas.width = window.innerWidth / 2;
    canvas.height = window.innerHeight;
}

window.addEventListener("resize", resize);
resize();

let t = 0;

function draw() {

    t += 0.01;

    ctx.clearRect(0,0,canvas.width,canvas.height);

    const g = ctx.createLinearGradient(0,0,0,canvas.height);

    g.addColorStop(0,"#103b73");
    g.addColorStop(.5,"#08233d");
    g.addColorStop(1,"#040b12");

    ctx.fillStyle = g;
    ctx.fillRect(0,0,canvas.width,canvas.height);

    ctx.strokeStyle="rgba(34,211,238,.18)";
    ctx.lineWidth=2;

    for(let i=0;i<12;i++){

        ctx.beginPath();

        for(let y=0;y<canvas.height;y+=8){

            const x=
                canvas.width/2
                +Math.sin(y*.003+t+i)*120
                +(i-6)*18;

            if(y===0)
                ctx.moveTo(x,y);
            else
                ctx.lineTo(x,y);

        }

        ctx.stroke();

    }

    requestAnimationFrame(draw);

}

draw();

})();
