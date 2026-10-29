const fs=require('fs'),path=require('path'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),editor=path.join(root,'tools/l2editor/L2Editor');
const pkg=path.join(root,'tools/l2editor/AmberParticlesV2/Classes');fs.mkdirSync(pkg,{recursive:true});
const asset=path.join(root,'exports/contract').replace(/\\/g,'/');
const imports=`#exec TEXTURE IMPORT NAME=AmberWhite FILE="${asset}/AmberWhite.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=AmberFire FILE="${asset}/AmberFire.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=Ring FILE="${asset}/Ring.tga" MIPS=OFF MASKED=1
#exec STATICMESH IMPORT NAME=ArrowWhite FILE="${asset}/AmberWhite.lwo"
#exec STATICMESH IMPORT NAME=ArrowFire FILE="${asset}/AmberFire.lwo"
#exec STATICMESH IMPORT NAME=ArrowSky FILE="${asset}/AmberSky.lwo"
#exec STATICMESH IMPORT NAME=ArrowShot FILE="${asset}/AmberShot.lwo"`;
const rootProps=`AutoDestroy=True\n    bNoDelete=False\n    bDirectional=True\n    bHidden=False\n    LifeSpan=2.0`;
for(const [name,mesh,count,z0,z1,velocity,life,scale] of [
 ['Rain','ArrowWhite',28,320,360,-600,1.1,1.8],['FireRain','ArrowFire',28,320,360,-600,1.1,1.8],
 ['SkyVolley','ArrowSky',12,35,45,900,.7,1.3],['FireShot','ArrowShot',1,0,0,0,.65,1.6]]) {
 const fire=name==='FireRain'||name==='FireShot';const shot=name==='FireShot',sky=name==='SkyVolley';
 const loc=shot?'X=(Min=0,Max=0),Y=(Min=0,Max=0),Z=(Min=0,Max=0)':`X=(Min=${sky?-5:-180},Max=${sky?5:180}),Y=(Min=${sky?-5:-180},Max=${sky?5:180}),Z=(Min=${z0},Max=${z1})`;
 const vel=shot?'X=(Min=1400,Max=1400)':`Z=(Min=${velocity},Max=${velocity})`;
 const color=fire?'R=255,G=105,B=15,A=255':'R=200,G=230,B=255,A=255';
 fs.writeFileSync(path.join(pkg,name+'.uc'),`class ${name} extends Emitter;
${imports}
defaultproperties
{
    Begin Object Class=MeshEmitter Name=Arrows
        StaticMesh=StaticMesh'AmberParticlesV2.${mesh}'
        UseParticleColor=False
        UseCollision=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=${sky?'18.0':'150.0'}
        MaxParticles=${count}
        RespawnDeadParticles=${sky?'True':'False'}
        StartLocationRange=(${loc})
        ${shot?'CoordinateSystem=PTCS_Relative':''}
        StartVelocityRange=(${vel})
        StartSizeRange=(X=(Min=${scale},Max=${scale}),Y=(Min=${scale},Max=${scale}),Z=(Min=${scale},Max=${scale}))
        LifetimeRange=(Min=${life},Max=${life})
        SecondsBeforeInactive=0.0
    End Object
    Emitters(0)=MeshEmitter'Arrows'
    Begin Object Class=SpriteEmitter Name=Glow
        Texture=Texture'AmberParticlesV2.${fire?'AmberFire':'AmberWhite'}'
        DrawStyle=PTDS_Brighten
        UseColorScale=True
        ColorScale(0)=(RelativeTime=0.0,Color=(${color}))
        ColorScale(1)=(RelativeTime=1.0,Color=(${color}))
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=${sky?'18.0':'150.0'}
        MaxParticles=${count}
        RespawnDeadParticles=${sky?'True':'False'}
        StartLocationRange=(${loc})
        ${shot?'CoordinateSystem=PTCS_Relative':''}
        StartVelocityRange=(${vel})
        StartSizeRange=(X=(Min=2,Max=2),Y=(Min=24,Max=24),Z=(Min=2,Max=2))
        LifetimeRange=(Min=${life},Max=${life})
        SecondsBeforeInactive=0.0
    End Object
    Emitters(1)=SpriteEmitter'Glow'
    ${sky?rootProps.replace('LifeSpan=2.0','LifeSpan=3.5'):rootProps}
}
`);
}
fs.writeFileSync(path.join(pkg,'ShotCharge.uc'),`class ShotCharge extends Emitter;
${imports}
defaultproperties
{
    Begin Object Class=SpriteEmitter Name=Sparks
        Texture=Texture'AmberParticlesV2.AmberWhite'
        DrawStyle=PTDS_Brighten
        CoordinateSystem=PTCS_Relative
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=120.0
        MaxParticles=18
        RespawnDeadParticles=False
        StartLocationRange=(X=(Min=-2,Max=2),Y=(Min=-2,Max=2),Z=(Min=-18,Max=18))
        StartVelocityRange=(X=(Min=-15,Max=15),Y=(Min=-15,Max=15),Z=(Min=-25,Max=25))
        StartSizeRange=(X=(Min=2,Max=4),Y=(Min=2,Max=4),Z=(Min=2,Max=4))
        LifetimeRange=(Min=0.35,Max=0.55)
        SecondsBeforeInactive=0.0
    End Object
    Emitters(0)=SpriteEmitter'Sparks'
    ${rootProps}
}
`);
fs.writeFileSync(path.join(pkg,'Mark.uc'),`class Mark extends Emitter;
${imports}
defaultproperties
{
    Begin Object Class=SpriteEmitter Name=Circle
        Texture=Texture'AmberParticlesV2.Ring'
        DrawStyle=PTDS_AlphaBlend
        UseDirectionAs=PTDU_Normal
        ProjectionNormal=(Z=1.0)
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=100.0
        MaxParticles=1
        RespawnDeadParticles=False
        StartLocationRange=(Z=(Min=8,Max=8))
        StartSizeRange=(X=(Min=200,Max=200),Y=(Min=200,Max=200),Z=(Min=200,Max=200))
        LifetimeRange=(Min=5.8,Max=5.8)
        SecondsBeforeInactive=0.0
    End Object
    Emitters(0)=SpriteEmitter'Circle'
    ${rootProps.replace('LifeSpan=2.0','LifeSpan=5.9')}
}
`);
const ini=fs.readFileSync(path.join(editor,'UT2003.ini'),'latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=AmberParticlesV2\n';
fs.writeFileSync(path.join(editor,'AmberParticlesV2.ini'),ini,'latin1');
const out=path.join(editor,'AmberParticlesV2.u');if(fs.existsSync(out))fs.unlinkSync(out);
const r=cp.spawnSync(path.join(editor,'UCC.exe'),['make','-Silent','-NoBind','ini=AmberParticlesV2.ini'],{cwd:editor,encoding:'utf8',timeout:180000,windowsHide:true});
fs.writeFileSync(path.join(root,'reports/amber-particles-v2-build.log'),(r.stdout||'')+(r.stderr||''));
if(r.error||r.status!==0||!fs.existsSync(out))throw Error('UCC failed: '+r.error+'; '+r.stdout);
console.log('AmberParticlesV2 compiled: bow charge, fire tracer, brighter descending arrows and fixed ground ring.');
