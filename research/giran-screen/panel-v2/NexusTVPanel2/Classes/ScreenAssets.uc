class ScreenAssets extends Actor;
#exec MESH MODELIMPORT MESH=Screen MODELFILE="E:/l2-local/research/giran-screen/panel-v2/assets/Screen.psk" LODSTYLE=0 LODSPECIFY=1
#exec MESH LODMODEL MESH=Screen LEVEL=0 DISTANCEFACTOR=0 REDUCTION=1 MAXINFLUENCES=1 COHERENCE=1
#exec MESHMAP SCALE MESHMAP=Screen X=1 Y=1 Z=1
#exec TEXTURE IMPORT NAME=Feed FILE="E:/l2-local/research/giran-screen/panel-v2/assets/Feed.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=Frame FILE="E:/l2-local/research/giran-screen/panel-v2/assets/Frame.tga" MIPS=OFF
#exec MESHMAP SETTEXTURE MESHMAP=Screen NUM=0 TEXTURE=Feed
#exec MESHMAP SETTEXTURE MESHMAP=Screen NUM=1 TEXTURE=Frame
defaultproperties
{
 DrawType=DT_Mesh
 Mesh=SkeletalMesh'NexusTVPanel2.Screen'
 bUnlit=True
}
