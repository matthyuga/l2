class EventGold extends Emitter;
#exec TEXTURE IMPORT NAME=EventLabel FILE="E:/l2-local/research/visual-effects/npc-labels/native-v1/EventLabel.tga" MIPS=OFF
#exec TEXTURE IMPORT NAME=GoldMote FILE="E:/l2-local/research/visual-effects/npc-labels/native-v1/GoldMote.tga" MIPS=OFF
defaultproperties
{
    Begin Object Class=SpriteEmitter Name=Label
        Texture=Texture'HellgamesLabelsV1.EventLabel'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Relative
        UseDirectionAs=PTDU_None
        UseCollision=False
        UniformSize=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=1.0
        MaxParticles=1
        RespawnDeadParticles=True
        SecondsBeforeInactive=0.0
        StartLocationRange=(Z=(Min=90.0,Max=90.0))
        StartSizeRange=(X=(Min=55.0,Max=55.0),Y=(Min=13.75,Max=13.75),Z=(Min=1.0,Max=1.0))
        LifetimeRange=(Min=3600.0,Max=3600.0)
    End Object
    Emitters(0)=SpriteEmitter'Label'
    Begin Object Class=SpriteEmitter Name=Motes
        Texture=Texture'HellgamesLabelsV1.GoldMote'
        DrawStyle=PTDS_AlphaBlend
        CoordinateSystem=PTCS_Relative
        UseDirectionAs=PTDU_None
        UseCollision=False
        AutomaticInitialSpawning=False
        InitialParticlesPerSecond=5.0
        MaxParticles=16
        RespawnDeadParticles=True
        SecondsBeforeInactive=0.0
        StartLocationRange=(X=(Min=-20.0,Max=20.0),Y=(Min=-20.0,Max=20.0),Z=(Min=68.0,Max=90.0))
        StartVelocityRange=(X=(Min=-1.0,Max=1.0),Y=(Min=-1.0,Max=1.0),Z=(Min=4.0,Max=7.0))
        StartSizeRange=(X=(Min=0.8,Max=1.8),Y=(Min=0.8,Max=1.8),Z=(Min=0.8,Max=1.8))
        FadeIn=True
        FadeInEndTime=0.4
        FadeOut=True
        FadeOutStartTime=1.8
        LifetimeRange=(Min=2.6,Max=3.2)
    End Object
    Emitters(1)=SpriteEmitter'Motes'
    AutoDestroy=False
    bNoDelete=False
    bHidden=False
    bDirectional=False
    LifeSpan=0.0
}
