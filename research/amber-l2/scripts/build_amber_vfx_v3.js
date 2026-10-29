const fs=require('fs'),path=require('path'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),editor=path.join(root,'tools/l2editor/L2Editor');
const pkg=path.join(root,'tools/l2editor/AmberParticlesV3/Classes');fs.mkdirSync(pkg,{recursive:true});
const asset=path.join(root,'exports/contract').replace(/\\/g,'/');
// Additive radial textures avoid square flashes without changing the existing arrow materials.
for(const [name,color] of [['GlowWhite',[210,235,255]],['GlowFire',[255,125,25]]]){
 const size=32,header=Buffer.alloc(18),pixels=Buffer.alloc(size*size*4);
 header[2]=2;header.writeUInt16LE(size,12);header.writeUInt16LE(size,14);header[16]=32;header[17]=0x28;
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const radius=Math.hypot((x+.5-size/2)/(size/2),(y+.5-size/2)/(size/2));
  const intensity=Math.pow(Math.max(0,1-radius),2),offset=(y*size+x)*4;
  pixels[offset]=Math.round(color[2]*intensity);pixels[offset+1]=Math.round(color[1]*intensity);pixels[offset+2]=Math.round(color[0]*intensity);pixels[offset+3]=255;
 }
 fs.writeFileSync(path.join(asset,name+'.tga'),Buffer.concat([header,pixels]));
}
const imports=`#exec TEXTURE IMPORT NAME=AmberWhite FILE="${asset}/AmberWhite.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=AmberFire FILE="${asset}/AmberFire.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=GlowWhite FILE="${asset}/GlowWhite.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=GlowFire FILE="${asset}/GlowFire.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=Ring FILE="${asset}/Ring.tga" MIPS=OFF MASKED=1
#exec STATICMESH IMPORT NAME=ArrowWhite FILE="${asset}/AmberWhite.lwo"
#exec STATICMESH IMPORT NAME=ArrowFire FILE="${asset}/AmberFire.lwo"
#exec STATICMESH IMPORT NAME=ArrowSky FILE="${asset}/AmberSky.lwo"
#exec STATICMESH IMPORT NAME=ArrowShot FILE="${asset}/AmberShot.lwo"`;
const positions=[];
for(const [radius,count] of [[50,6],[115,10],[175,14]])for(let i=0;i<count;i++){
 const angle=2*Math.PI*(i+.5)/count;
 positions.push({x:+(radius*Math.cos(angle)).toFixed(3),y:+(radius*Math.sin(angle)).toFixed(3)});
}
const actor=(name,components,life=2)=>`class ${name} extends Emitter;
${imports}
defaultproperties
{
${components.map((c,i)=>c+`\n    Emitters(${i})=${c.includes('Class=MeshEmitter')?'MeshEmitter':'SpriteEmitter'}'P${i}'`).join('\n')}
    AutoDestroy=True
    bNoDelete=False
    bDirectional=True
    bHidden=False
    LifeSpan=${life}
}
`;
const spawning=`AutomaticInitialSpawning=False
        InitialParticlesPerSecond=10000.0
        RespawnDeadParticles=False
        SecondsBeforeInactive=0.0`;
function arrow(i,mesh,x,y,z,vz,life,scale){return `    Begin Object Class=MeshEmitter Name=P${i}
        StaticMesh=StaticMesh'AmberParticlesV3.${mesh}'
        UseParticleColor=False
        UseCollision=False
        CoordinateSystem=PTCS_Absolute
        MaxParticles=1
        StartLocationRange=(X=(Min=${x},Max=${x}),Y=(Min=${y},Max=${y}),Z=(Min=${z},Max=${z}))
        StartVelocityRange=(Z=(Min=${vz},Max=${vz}))
        StartSizeRange=(X=(Min=${scale},Max=${scale}),Y=(Min=${scale},Max=${scale}),Z=(Min=${scale},Max=${scale}))
        LifetimeRange=(Min=${life},Max=${life})
        ${spawning}
    End Object`;}
function glow(i,fire,x,y,z,life=.4,scale=6,max=4,relative=false){return `    Begin Object Class=SpriteEmitter Name=P${i}
        Texture=Texture'AmberParticlesV3.${fire?'GlowFire':'GlowWhite'}'
        DrawStyle=PTDS_Brighten
        CoordinateSystem=${relative?'PTCS_Relative':'PTCS_Absolute'}
        UseColorScale=True
        ColorScale(0)=(RelativeTime=0.0,Color=(R=255,G=${fire?115:230},B=${fire?25:255},A=255))
        ColorScale(1)=(RelativeTime=1.0,Color=(R=255,G=${fire?40:180},B=${fire?0:255},A=0))
        FadeOut=True
        FadeOutStartTime=${life*.35}
        MaxParticles=${max}
        StartLocationRange=(X=(Min=${x-4},Max=${x+4}),Y=(Min=${y-4},Max=${y+4}),Z=(Min=${z-4},Max=${z+4}))
        StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=10,Max=45))
        StartSizeRange=(X=(Min=${scale*.5},Max=${scale}),Y=(Min=${scale*.5},Max=${scale}),Z=(Min=${scale*.5},Max=${scale}))
        LifetimeRange=(Min=${life},Max=${life})
        ${spawning}
    End Object`;}
// One deterministic wave. The lowest mesh vertex is -32; 1.25 * 32 = 40.
// Its tip reaches the floor at (430 - 40) / 600 = 0.650 seconds.
for(const fire of [false,true]){
 const name=fire?'FireRain':'Rain';
 fs.writeFileSync(path.join(pkg,name+'.uc'),actor(name,positions.map((p,i)=>arrow(i,fire?'ArrowFire':'ArrowWhite',p.x,p.y,430,-600,.650,1.25)),1));
 fs.writeFileSync(path.join(pkg,name+'Impact.uc'),actor(name+'Impact',positions.map((p,i)=>glow(i,fire,p.x,p.y,8,.4,fire?9:6,4)),1));
}
const sky=arrow(0,'ArrowSky',0,0,45,900,.7,1.3)
 .replace('MaxParticles=1','MaxParticles=12').replace('InitialParticlesPerSecond=10000.0','InitialParticlesPerSecond=18.0').replace('RespawnDeadParticles=False','RespawnDeadParticles=True');
fs.writeFileSync(path.join(pkg,'SkyVolley.uc'),actor('SkyVolley',[sky],3.5));
fs.writeFileSync(path.join(pkg,'ShotCharge.uc'),actor('ShotCharge',[glow(0,false,0,0,0,.55,10,24,true)],1));
fs.writeFileSync(path.join(pkg,'FireIgnite.uc'),actor('FireIgnite',[glow(0,true,0,0,0,.85,14,32,true)],1.3));
// Cosmetic tracer lengths use 50-unit bands; native Attack still owns hit/miss/damage.
for(let level=1;level<=16;level++){
 const life=(level*50/1400).toFixed(6);
 const component=arrow(0,'ArrowShot',0,0,0,0,life,1.25)
  .replace('CoordinateSystem=PTCS_Absolute','CoordinateSystem=PTCS_Relative')
  .replace('StartVelocityRange=(Z=(Min=0,Max=0))','StartVelocityRange=(X=(Min=1400,Max=1400))');
 fs.writeFileSync(path.join(pkg,`FireShot${level}.uc`),actor(`FireShot${level}`,[component],1));
}
const mark=`    Begin Object Class=SpriteEmitter Name=P0
        Texture=Texture'AmberParticlesV3.Ring'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Absolute
        UseDirectionAs=PTDU_Normal
        ProjectionNormal=(Z=1.0)
        MaxParticles=1
        StartLocationRange=(Z=(Min=8,Max=8))
        StartSizeRange=(X=(Min=200,Max=200),Y=(Min=200,Max=200),Z=(Min=200,Max=200))
        LifetimeRange=(Min=5.8,Max=5.8)
        ${spawning}
    End Object`;
fs.writeFileSync(path.join(pkg,'Mark.uc'),actor('Mark',[mark],5.9));
const manifest={rainRadius:200,positions,arrowTipZ:-32,scale:1.25,startZ:430,velocityZ:-600,fallMs:650,waves:3,waveIntervalMs:500,tracerSpeed:1400,tracerDistanceStep:50,tracerLevels:16};
const stage=path.join(root,'exports/contract/combat-vfx-v3');fs.mkdirSync(stage,{recursive:true});
fs.writeFileSync(path.join(stage,'trajectory.json'),JSON.stringify(manifest,null,2));
const ini=fs.readFileSync(path.join(editor,'UT2003.ini'),'latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberParticlesV3\n';
fs.writeFileSync(path.join(editor,'AmberParticlesV3.ini'),ini,'latin1');
const out=path.join(editor,'AmberParticlesV3.u');
if(fs.existsSync(out))fs.unlinkSync(out);
const r=cp.spawnSync(path.join(editor,'UCC.exe'),['make','-Silent','-NoBind','ini=AmberParticlesV3.ini'],{cwd:editor,encoding:'utf8',timeout:180000,windowsHide:true});
fs.writeFileSync(path.join(root,'reports/amber-particles-v3-build.log'),(r.stdout||'')+(r.stderr||''));
if(r.error||r.status!==0||!fs.existsSync(out))throw Error('UCC failed: '+r.error+'; '+r.stdout+'; '+r.stderr);
console.log('PASS: AmberParticlesV3 compiled; circular rain, synchronized ground impacts, bow charge and fire ignition.');
