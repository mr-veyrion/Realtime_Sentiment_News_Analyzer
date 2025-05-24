   // File: static/js/globe.js
   document.addEventListener('DOMContentLoaded', () => {
    const globeContainer = document.getElementById('globe');
    if (!globeContainer) {
        console.error('Globe container element not found');
        return;
    }
    console.log('Globe container dimensions:', globeContainer.offsetWidth, globeContainer.offsetHeight);

    let selectedCity = 'all';
    
    // Create scene and set a background color (not pure black to help with contrast)
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x101010);

    // Initialize Globe with country features
    const Globe = new ThreeGlobe({ animateIn: true })
        .globeImageUrl('https://unpkg.com/three-globe@2.24.7/example/img/earth-blue-marble.jpg')
        .bumpImageUrl('https://unpkg.com/three-globe@2.24.7/example/img/earth-topology.png')
        .polygonsData('https://unpkg.com/three-globe@2.24.7/example/countries.geojson')
        .polygonCapColor(() => 'rgba(200, 200, 200, 0.3)')
        .polygonSideColor(() => 'rgba(0, 0, 0, 0)')
        .showPolygonGraticules(true);
    scene.add(Globe);

    // Add ambient and directional lights for proper illumination.
    const ambientLight = new THREE.AmbientLight(0xcccccc, 1);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Setup camera with an aspect ratio matching the container.
    const camera = new THREE.PerspectiveCamera(45, globeContainer.offsetWidth / globeContainer.offsetHeight, 0.1, 1000);
    camera.position.set(0, 0, 400);

    // Setup WebGL renderer.
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(globeContainer.offsetWidth, globeContainer.offsetHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    globeContainer.appendChild(renderer.domElement);

    // Use OrbitControls to enable user interaction.
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.8;
    controls.zoomSpeed = 0.8;

    // Update renderer size on window resize.
    window.addEventListener('resize', () => {
        const width = globeContainer.offsetWidth;
        const height = globeContainer.offsetHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
        console.log('Resized renderer to:', width, height);
    });

    // Enhanced city rotation with smooth transition
    function animateCameraTo(lng, lat) {
        const phi = (90 - lat) * (Math.PI/180);
        const theta = (lng + 180) * (Math.PI/180);
        const targetPosition = {
            x: 400 * Math.sin(phi) * Math.cos(theta),
            y: 400 * Math.cos(phi),
            z: 400 * Math.sin(phi) * Math.sin(theta)
        };
        
        // Smooth transition
        controls.autoRotate = false;
        controls.target.set(0, 0, 0);
        new TWEEN.Tween(camera.position)
            .to(targetPosition, 1500)
            .easing(TWEEN.Easing.Quadratic.InOut)
            .start();
    }

    // Animation loop
    (function animate() {
        TWEEN.update();
        controls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    })();

    // Handle city selection
    document.getElementById('citySelector').addEventListener('change', function(e) {
        selectedCity = e.target.value;
        document.querySelectorAll('.city-card').forEach(card => {
            card.style.display = (selectedCity === 'all' || card.id.includes(selectedCity)) ? 'block' : 'none';
        });
        
        // Rotate globe to selected city (approximation with OrbitControls)
        const cityCoordinates = {
            'bangalore': [77.5946, 12.9716],
            'mumbai': [72.8777, 19.0760],
            'delhi': [77.1025, 28.7041]
        };
        
        if (cityCoordinates[selectedCity]) {
            const [lng, lat] = cityCoordinates[selectedCity];
            animateCameraTo(lng, lat);
            console.log(`Camera repositioned for ${selectedCity}:`, camera.position);
        }
    });
});