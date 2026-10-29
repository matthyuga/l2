// Experimental client adapter. Only the dedicated Behemoth NPC uses this class.
class BehemothRide extends Pawn;

var int DriverId, GunnerId;
var Pawn DriverPawn, GunnerPawn;
var bool DriverWasHard, GunnerWasHard;
var float SearchElapsed;

function ReadSeats()
{
    local string Payload;
    local int Separator;
    if (Left(nickname,4) != "BHM:") return;
    Payload=Mid(nickname,4);
    Separator=InStr(Payload,":");
    if (Separator < 0) return;
    DriverId=int(Left(Payload,Separator));
    GunnerId=int(Mid(Payload,Separator+1));
    // Keep transport metadata out of the visible NPC label.
    nickname="Behemoth";
}

function ReleaseRider(Pawn P, bool WasHard)
{
    if (P == None) return;
    DetachFromBone(P);
    if (P.Base == Self) P.SetBase(None);

}

function BindRider(Pawn P, vector BoneOffset, bool IsDriver)
{
    local rotator R;
    local name Pose;
    if (P == None || P.bDeleteMe) return;
    if (P.Base != Self)
    {
        if (IsDriver) DriverWasHard=P.bHardAttach;
        else GunnerWasHard=P.bHardAttach;

        if (!AttachToBone(P,'Bip01 Spine1'))
        {

            return;
        }
        P.SetRelativeLocation(BoneOffset);
    }
    if (IsDriver)
    {
        R.Yaw=0;
        P.SetRelativeRotation(R);
        Pose='None';
        if (P.HasAnim('Strider_FFighter')) Pose='Strider_FFighter';
        else if (P.HasAnim('Strider_MFighter')) Pose='Strider_MFighter';
        else if (P.HasAnim('Strider_FElf')) Pose='Strider_FElf';
        else if (P.HasAnim('Strider_MElf')) Pose='Strider_MElf';
        else if (P.HasAnim('Strider_FDarkElf')) Pose='Strider_FDarkElf';
        else if (P.HasAnim('Strider_MDarkElf')) Pose='Strider_MDarkElf';
        else if (P.HasAnim('Strider_FDwarf')) Pose='Strider_FDwarf';
        else if (P.HasAnim('Strider_MDwarf')) Pose='Strider_MDwarf';
        else if (P.HasAnim('Strider_FOrc')) Pose='Strider_FOrc';
        else if (P.HasAnim('Strider_MOrc')) Pose='Strider_MOrc';
        else if (P.HasAnim('Strider_FMagic')) Pose='Strider_FMagic';
        else if (P.HasAnim('Strider_MMagic')) Pose='Strider_MMagic';
        if (Pose != 'None' && P.HasAnim(Pose)) P.LoopAnim(Pose,1,0.15);
    }
}

event Tick(float Delta)
{
    local Pawn P;
    local vector DriverOffset,GunnerOffset;
    Super.Tick(Delta);
    ReadSeats();
    if (DriverPawn != None && (DriverPawn.L2ServerObjectID != DriverId || DriverPawn.bDeleteMe))
    { ReleaseRider(DriverPawn,DriverWasHard); DriverPawn=None; }
    if (GunnerPawn != None && (GunnerPawn.L2ServerObjectID != GunnerId || GunnerPawn.bDeleteMe))
    { ReleaseRider(GunnerPawn,GunnerWasHard); GunnerPawn=None; }
    SearchElapsed+=Delta;
    if (SearchElapsed >= 0.25)
    {
        SearchElapsed=0;
        foreach DynamicActors(class'Pawn',P)
        {
            if (P != Self && P.L2ServerObjectID == DriverId && DriverId > 0) DriverPawn=P;
            if (P != Self && P.L2ServerObjectID == GunnerId && GunnerId > 0) GunnerPawn=P;
        }
    }
    DriverOffset.X=23.9693; DriverOffset.Y=-43.5524; DriverOffset.Z=0;
    GunnerOffset.X=-22.1000; GunnerOffset.Y=-42.4621; GunnerOffset.Z=0;
    BindRider(DriverPawn,DriverOffset,true);
    BindRider(GunnerPawn,GunnerOffset,false);
}

event Destroyed()
{
    ReleaseRider(DriverPawn,DriverWasHard);
    ReleaseRider(GunnerPawn,GunnerWasHard);
    Super.Destroyed();
}

defaultproperties
{
    bStatic=False
    DrawType=DT_Mesh
    Mesh=SkeletalMesh'BHMTransport.BehemothMesh'
}
