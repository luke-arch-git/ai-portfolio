import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const container = document.getElementById('viewer');
const loading = document.getElementById('loading');
const progress = document.getElementById('progress');
const loadValue = document.getElementById('load-value');
const rotateButton = document.getElementById('rotate');
const wireButton = document.getElementById('wireframe');
const modal = document.getElementById('hero-modal');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe5e0d6);
const camera = new THREE.PerspectiveCamera(34, 1, 0.05, 200);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
scene.environment = pmrem.fromScene(room, 0.04).texture;
room.dispose();
pmrem.dispose();

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.065;
controls.autoRotate = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
controls.autoRotateSpeed = 0.65;
controls.minDistance = 4.2;
controls.maxDistance = 15;
controls.minPolarAngle = 0.04;
controls.maxPolarAngle = Math.PI - 0.04;
controls.enablePan = true;
controls.panSpeed = 0.5;
rotateButton.classList.toggle('active', controls.autoRotate);
rotateButton.setAttribute('aria-pressed', String(controls.autoRotate));

scene.add(new THREE.HemisphereLight(0xfff5e7, 0x64717b, 1.25));
const key = new THREE.DirectionalLight(0xffe4c8, 3.0);
key.position.set(-4, 8, 6);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = -5;
key.shadow.camera.right = 5;
key.shadow.camera.top = 7;
key.shadow.camera.bottom = -3;
key.shadow.bias = -0.0004;
scene.add(key);
const fill = new THREE.DirectionalLight(0xb8e5ff, 1.4);
fill.position.set(6, 4, 2);
scene.add(fill);
const rim = new THREE.DirectionalLight(0xffb17f, 2.4);
rim.position.set(1, 6, -5);
scene.add(rim);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ color: 0x4b4842, opacity: 0.18 }));
ground.rotation.x = -Math.PI / 2;
ground.position.y = 0.18;
ground.receiveShadow = true;
scene.add(ground);

const shadowCanvas = document.createElement('canvas');
shadowCanvas.width = shadowCanvas.height = 256;
const ctx = shadowCanvas.getContext('2d');
const gradient = ctx.createRadialGradient(128, 128, 5, 128, 128, 124);
gradient.addColorStop(0, 'rgba(34,42,45,.24)');
gradient.addColorStop(0.4, 'rgba(34,42,45,.12)');
gradient.addColorStop(1, 'rgba(34,42,45,0)');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 256, 256);
const contact = new THREE.Mesh(new THREE.PlaneGeometry(3.8, 3.8), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(shadowCanvas), transparent: true, depthWrite: false }));
contact.rotation.x = -Math.PI / 2;
contact.position.y = 0.184;
scene.add(contact);

let model;
let initialPosition;
let initialTarget;
const materials = new Set();

function setWireframe(value) {
  materials.forEach((material) => {
    material.wireframe = value;
    material.needsUpdate = true;
  });
}

function fitCamera() {
  const box = new THREE.Box3().setFromObject(model);
  const center = box.getCenter(new THREE.Vector3());
  controls.target.copy(center);
  camera.position.copy(center).add(new THREE.Vector3(5.7, 2.65, 8.6));
  camera.lookAt(center);
  controls.update();
  initialPosition = camera.position.clone();
  initialTarget = center.clone();
}

new GLTFLoader().load('../output/STARLING-01.glb', (gltf) => {
  model = gltf.scene;
  model.traverse((object) => {
    if (!object.isMesh) return;
    object.castShadow = true;
    object.receiveShadow = true;
    const objectMaterials = Array.isArray(object.material) ? object.material : [object.material];
    objectMaterials.forEach((material) => {
      materials.add(material);
      material.envMapIntensity = 0.85;
      if (material.name.includes('Deep titanium')) {
        material.color.set(0x303844);
        material.roughness = 0.36;
        material.envMapIntensity = 0.55;
      }
      if (material.transmission > 0) {
        material.thickness = 0.12;
        material.ior = 1.46;
        material.attenuationColor = new THREE.Color(0x65d9e6);
        material.attenuationDistance = 2.5;
      }
    });
  });
  scene.add(model);
  fitCamera();
  progress.style.width = '100%';
  loadValue.textContent = '100%';
  requestAnimationFrame(() => loading.classList.add('done'));
}, (event) => {
  const value = event.total ? Math.round(event.loaded / event.total * 100) : Math.min(95, Math.round(event.loaded / 11938152 * 100));
  progress.style.width = `${value}%`;
  loadValue.textContent = `${value}%`;
}, (error) => {
  console.error(error);
  loading.querySelector('p').textContent = 'MODEL LOAD FAILED · PLEASE USE A LOCAL SERVER';
  loadValue.textContent = 'GLB NOT FOUND';
});

controls.addEventListener('start', () => {
  if (!controls.autoRotate) return;
  controls.autoRotate = false;
  rotateButton.classList.remove('active');
  rotateButton.setAttribute('aria-pressed', 'false');
});

rotateButton.addEventListener('click', () => {
  controls.autoRotate = !controls.autoRotate;
  rotateButton.classList.toggle('active', controls.autoRotate);
  rotateButton.setAttribute('aria-pressed', String(controls.autoRotate));
});
wireButton.addEventListener('click', () => {
  const value = wireButton.getAttribute('aria-pressed') !== 'true';
  wireButton.setAttribute('aria-pressed', String(value));
  wireButton.classList.toggle('active', value);
  setWireframe(value);
});
document.getElementById('reset').addEventListener('click', () => {
  if (!initialPosition) return;
  camera.position.copy(initialPosition);
  controls.target.copy(initialTarget);
  controls.update();
});
document.getElementById('compare').addEventListener('click', () => modal.showModal());
document.getElementById('close-modal').addEventListener('click', () => modal.close());
modal.addEventListener('click', (event) => {
  if (event.target === modal) modal.close();
});

function resize() {
  const width = container.clientWidth;
  const height = container.clientHeight;
  if (!width || !height) return;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(container);
resize();
renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
