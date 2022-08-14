const sse = new EventSource('https://dplace.up.railway.app/api/fetch');
    sse.addEventListener("notice", function(e) {
    console.log(e.data)
    })
    sse.addEventListener("update", function(e) {
    console.log(e.data)
    })
    sse.addEventListener("new_pixels", function(e) {
    pixels = JSON.parse(e.data);
    const zoomIntensity = 0.1;
    const canvas = document.getElementById("myCanvas");
    // https://stackoverflow.com/questions/2916081/zoom-in-on-a-point-using-scale-and-translate
    let context = canvas.getContext("2d");
    const width = 960;
    const height = 540;
    var recsize = 1;

    let scale = 1;
    let originx = 0;
    let originy = 0;
    let visibleWidth = width;
    let visibleHeight = height;


    function draw(){
        context.fillStyle = "white";
        context.fillRect(originx, originy, width/scale, height/scale);
        pixels.forEach(function(p){
            context.fillStyle = p.colour;
            context.fillRect(p.x*recsize, p.y*recsize, recsize, recsize);
        });
        // Schedule the redraw for the next display refresh.
        window.requestAnimationFrame(draw);
    }
    // Begin the animation loop.
    draw();

    canvas.onwheel = function (event){
        event.preventDefault();
        // Get mouse offset.
        const mousex = event.clientX - canvas.offsetLeft;
        const mousey = event.clientY - canvas.offsetTop;
        // Normalize mouse wheel movement to +1 or -1 to avoid unusual jumps.
        const wheel = event.deltaY < 0 ? 1 : -1;

        // Compute zoom factor.
        const zoom = Math.exp(wheel * zoomIntensity);
        
        // Translate so the visible origin is at the context's origin.
        context.translate(originx, originy);
        
        // Compute the new visible origin. Originally the mouse is at a
        // distance mouse/scale from the corner, we want the point under
        // the mouse to remain in the same place after the zoom, but this
        // is at mouse/new_scale away from the corner. Therefore we need to
        // shift the origin (coordinates of the corner) to account for this.
        originx -= mousex/(scale*zoom) - mousex/scale;
        originy -= mousey/(scale*zoom) - mousey/scale;
        
        // Scale it (centered around the origin due to the trasnslate above).
        context.scale(zoom, zoom);
        // Offset the visible origin to it's proper position.
        context.translate(-originx, -originy);

        // Update scale and others.
        scale *= zoom;
        visibleWidth = width / scale;
        visibleHeight = height / scale;
    }
})