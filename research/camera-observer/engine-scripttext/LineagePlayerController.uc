//=============================================================================
// PlayerController
//
// PlayerControllers are used by human players to control pawns.
//
// This is a built-in Unreal class and it shouldn't be modified.
//=============================================================================
class LineagePlayerController extends PlayerController
	native;

var config	int		CheatFlyYaw;
var config	bool	bUseAutoTrackingPawn;		//ÀÚµ¿ÃßÀûÀ» »ç¿ëÇÒ °ÍÀÎÁö?
var config	bool	bUseVolumeCamera;			//VolumeCamera¸¦ »ç¿ëÇÒ °ÍÀÎÁö?
var config	bool	bUseHitCheckCamera;			//HitCheckCamera¸¦ »ç¿ëÇÒ °ÍÀÎÁö?
var config	float	AutoTrackingPawnSpeed;		//ÀÚµ¿ÃßÀû ¼Óµµ
var config	int		VolumeCameraRadius;			//VolumeCameraÀÇ Rotation
var config	int		HitCheckCameraMinDist;		//HitCheckCamera¸¦ »ç¿ëÇÏÁö ¾ÊÀ» ¶§ÀÇ ÃÖ¼Ò°ª
var config	int		FixedDefaultViewNum;		//°íÁ¤µÈ DefaultCamera °¹¼ö
var config	int		FixedDefaultCameraYaw[10];
var config	int		FixedDefaultCameraPitch[10];
var config	float	FixedDefaultCameraDist[10];
var config	float	FixedDefaultCameraViewHeight[10];
var config	int		FixedDefaultCameraHidePlayer[10];
var config	int		FixedDefaultCameraDisableZoom[10];
var	config	float	CameraViewHeightAdjust;		//ViewTarget ³ôÀÌÁ¶Àý

var			bool	bDisableCameraManuallyRotating;//Ä«¸Þ¶óÀÇ Manually È¸ÀüÀ» DisableÇÏ´ÂÁö?
var			bool	bCameraManuallyRotating;	//Ä«¸Þ¶ó°¡ Manually È¸ÀüÇØ¾ßÇÏ´ÂÁö?
var			bool	bFixView;					//°íÁ¤ Ä«¸Þ¶óÀÎÁö?
var			bool	bCameraMovingToDefault;		//Camera°¡ Default·Î ÀÌµ¿ÁßÀÎÁö?
var			bool	bUseDefaultCameraYaw;		//DefalutCamera°¡ Yaw¸¦ »ç¿ëÇÏ´ÂÁö?
var			bool	bUseDefaultCameraPitch;		//DefalutCamera°¡ Pitch¸¦ »ç¿ëÇÏ´ÂÁö?
var			bool	bUseDefaultCameraDist;		//DefalutCamera°¡ Dist¸¦ »ç¿ëÇÏ´ÂÁö?
var			bool	bDisableZoom;				

var			float	OldZoomingDist;				//ÀÌÀü Tick¿¡¼­ÀÇ ZoomingDist
var			vector	OldCameraLocation;			//ÀÌÀü Tick¿¡¼­ÀÇ CameraLocation
var			rotator	OldCameraRotation;			//ÀÌÀü Tick¿¡¼­ÀÇ CameraRotation
var			vector	OldViewTargetLocation;		//ÀÌÀü Tick¿¡¼­ÀÇ ViewTargetLocation

var			float	ManuallyCameraYaw;			//Ä«¸Þ¶óÀÇ Manually Yaw È¸Àü°ª
var			float	ManuallyCameraPitch;		//Ä«¸Þ¶óÀÇ Manually Pitch È¸Àü°ª
var			float	CurZoomingDist;				//ÇöÀç Zoom °Å¸®
var			float	DesiredZoomingDist;			//User ÀÔ·Â Zoom °Å¸®
var			int		DesiredPitch;				//User ÀÔ·Â Pitch
var			int		CurVolumeCameraRadius;		//ÇöÀç Zoom °Å¸®

var			int		CurFixedDefaultCameraNo;	//ÇöÀçÀÇ °íÁ¤µÈ DefaultCamera ¹øÈ£
var			int		DefaultCameraYaw;			//bDefaultCameraÀÇ ¸ñÇ¥ Yaw
var			int		DefaultCameraPitch;			//bDefaultCameraÀÇ ¸ñÇ¥ Pitch
var			float	DefaultCameraDist;			//bDefaultCameraÀÇ ¸ñÇ¥ Dist

var			bool	bCameraSpecialMove;
var			bool	bCameraMovingToSpecial;
var			int		SpecialCameraYaw;
var			int		SpecialCameraPitch;
var			float	SpecialCameraDist;
var			float	SpecialCameraDistSpeed;
var			INT		SpecialCameraYawSpeed;
var			INT		SpecialCameraPitchSpeed;
var			float	SpecialCameraDuration;
var			int		SpecialCurCameraYaw;
var			int		SpecialCurCameraPitch;
var			float	SpecialCurCameraDist;

var			int		CameraRelYaw;
var			int		CameraRelPitch;
var			int		CameraRelYawSpeed;
var			int		CameraRelPitchSpeed;
var			int		CameraCurRelYaw;
var			int		CameraCurRelPitch;
// var			bool	bRenderWide;

var			int		SavedViewTargetYaw;			//bDefaultCamera°¡ ½ÇÇàµÇ´Â ¼ø°£ÀÇ ViewTargetÀÇ Yaw
var			int		SavedViewTargetPitch;		//bDefaultCamera°¡ ½ÇÇàµÇ´Â ¼ø°£ÀÇ ViewTargetÀÇ Pitch

var			float	ValidateLocationTime;

var			float	TurningPendingTime;
var			bool	bKeyboardMoving;
var			bool	bKeyboardMovingPermanently;
var			bool	bDesiredKeyboardMoving;
var			bool	bDesiredKeyboardMovingPermanently;
var			int		KeyboardMovingDir;
var			int		KeyboardMovingDirFlg;
var			float	KeyboardMovingPendingTime;
var			bool	bJoypadMoving;
var			bool	bDesiredJoypadMoving;
var			bool	bDesiredJoypadMovingPermanently;
var			int		JoypadMovingDir;
var			float	JoypadMovingPendingTime;
var			bool	ShouldTurnToMovingDir;

//#ifdef __L2 //kurt
var	config	float   MaxZoomingDist;
var	config	float   MinZoomingDist;
struct NViewShakePtr
{
	var	int		Ptr;
};
var array<NViewShakePtr>	NViewShake;
struct NViewShakeMgrPtr
{
	var	int		Ptr;
};
var array<NViewShakeMgrPtr>	NViewShakeMgr;
//#endif

//#ifdef __L2 // zodiac
var bool			bObserverModeOn;
var bool			bBroadcastObserverModeOn;
var MusicVolume		MusicVolume;
var bool			bCanPlayMusic;
var float			MusicWaitTime;
var float			DefaultMusicWaitTime;
var int				MusicHandle;
var int				VoiceHandle;
var bool			bVehicleStart;
var bool			bGetServerMusic;
var int				nGetServerVoice;
var float			PlayMusicDelay;
var float			PlayVoiceDelay;
var bool			bLockMusic;
var string			bServerMusicName;
var string			bServerVoiceName;
//#endif

//#ifdef __L2 // idearain
var bool			bCameraWalking;				// CameraWalkingMode ÀÎÁö?
var Actor			CameraModeTarget;
//#endif
//#ifdef __L2 // gigadeth
var float			ManuallyCameraSpeed;	// Ä«¸Þ¶ó È¸Àü½Ã ¼Óµµ Default=1.0
//#endif

//#ifdef __L2 // by nonblock
var(AirVolume) AirEmitter			AirEffect;
//var(AirVolume) transient	name	RecentAirEffect;
//var(AirVolume) transient	bool	bWasInAirVolume;
//var(AirVolume) transient	float	TimeTouching;
//var(AirVolume) transient	bool	DoNotSpawn;				// don't try to spawn aireffect until the player leaves the volume.
//#endif

event PostBeginPlay()
{
	Super.PostBeginPlay();
//#ifdef __L2 // zodiac
	//UnderWaterLoopSound = sound(DynamicLoadObject("AmbSound.under_water", class'sound'));
	UnderWaterLoopSound = sound(DynamicLoadObject("ChrSound.UnderWater_Loop", class'sound'));
//#endif

	CurVolumeCameraRadius = VolumeCameraRadius;
}

function name GetMoveSeqName()
{
	return Pawn.RunAnimName[0];
}

function name GetWaitSeqName()
{
	return Pawn.WaitAnimName[0];
}

exec function HidePlayerPawn()
{
	Pawn.bHidden = true;
}

exec function ShowPlayerPawn()
{
	Pawn.bHidden = false;
}

exec function SetFlyYaw(int Value)
{
	CheatFlyYaw = Value;
}

exec function CameraRotationOn()
{
	if( bCameraMovingToSpecial || bCameraSpecialMove || bDisableCameraManuallyRotating || bCameraMovingToDefault ) return;
	bCameraManuallyRotating = true;
}

exec function CameraRotationOff()
{
	bCameraManuallyRotating = false;
}

exec function UseAutoTrackingPawnOn()
{
	bUseAutoTrackingPawn = true;
}

exec function UseAutoTrackingPawnOff()
{
	bUseAutoTrackingPawn = false;
}

exec function UseHitCheckCameraOn()
{
	bUseHitCheckCamera = true;
}

exec function UseHitCheckCameraOff()
{
	bUseHitCheckCamera = false;
}

exec function SetHitCheckCameraMinDist(int Delta)
{
	HitCheckCameraMinDist += Delta;
}

exec function ViewFix()
{
	if( bFixView ) bFixView = false;
	else bFixView = true;
}

function UpdateRotation(float DeltaTime, float maxPitch)
{
	local rotator ViewRotation;

	if( !bCheatFlying ) return;
	if( VSize(Pawn.Velocity) < 1.0f )
	{
		if( (Pawn.Rotation.Pitch&65535) == 0 ) return;
		ViewRotation = Pawn.Rotation;
		ViewRotation.Pitch = 0;
	}
	else ViewRotation = Rotation;
	ViewRotation.Yaw += CheatFlyYaw;

	//TurnTarget = None;
	//bRotateToDesired = false;
	//bSetTurnRot = false;
	//ViewRotation.Yaw += 32.0 * DeltaTime * aTurn;

	//SetRotation(ViewRotation);
	//Pawn.SetRotation(ViewRotation);
	Pawn.DesiredRotation = ViewRotation;
}

function bool CalcCameraMovingToDefaultYaw( float DeltaTime, int TargetYaw )
{
	local int BackYaw, temp;

	if( (TargetYaw + DefaultCameraYaw - OldCameraRotation.Yaw) % 65536 == 0 ) return false;

	temp = TargetYaw + DefaultCameraYaw - OldCameraRotation.Yaw;
	while( temp > 32768 ) temp -= 65536;
	while( temp < -32767 ) temp += 65536;

	if( -600 <= temp && temp < 0 ) BackYaw = int( -5000.0*DeltaTime );
	else if( 0 < temp && temp <= 600 ) BackYaw = int( 5000.0*DeltaTime );
	else BackYaw = int( float(temp)/6.0*50.0*DeltaTime );
	
	if( temp > 0 && BackYaw > temp ) BackYaw = temp;
	if( temp < 0 && BackYaw < temp ) BackYaw = temp;

	OldCameraRotation.Yaw += BackYaw;
	while( OldCameraRotation.Yaw > 32768 ) OldCameraRotation.Yaw -= 65536;
	while( OldCameraRotation.Yaw < -32767 ) OldCameraRotation.Yaw += 65536;

	return true;
}

function bool CalcCameraMovingToDefaultPitch( float DeltaTime, int TargetPitch )
{
	local int BackPitch, temp;

	if( (TargetPitch + DefaultCameraPitch - OldCameraRotation.Pitch) % 65536 == 0 ) return false;

	temp = TargetPitch + DefaultCameraPitch - OldCameraRotation.Pitch;
	while( temp > 32768 ) temp -= 65536;
	while( temp < -32767 ) temp += 65536;

	if( -600 <= temp && temp < 0 ) BackPitch = int( -5000.0*DeltaTime );
	else if( 0 < temp && temp <= 600 ) BackPitch = int( 5000.0*DeltaTime);
	else BackPitch = int( float(temp)/6.0*50.0*DeltaTime );
	
	if( temp > 0 && BackPitch > temp ) BackPitch = temp;
	if( temp < 0 && BackPitch < temp ) BackPitch = temp;

	OldCameraRotation.Pitch += BackPitch;
	while( OldCameraRotation.Pitch > 32768 ) OldCameraRotation.Pitch -= 65536;
	while( OldCameraRotation.Pitch < -32767 ) OldCameraRotation.Pitch += 65536;
	DesiredPitch = OldCameraRotation.Pitch;

	return true;
}

function bool CalcCameraMovingToDefaultDistance( float DeltaTime )
{
	local float temp, BackDist;

	if( CurZoomingDist+250.0 == DefaultCameraDist ) return false;

	temp = DefaultCameraDist - (CurZoomingDist+250.0);

	if( -6.0 <= temp && temp < 0.0 ) BackDist = -50.0*DeltaTime;
	else if( 0.0 < temp && temp <= 6.0 ) BackDist = 50.0*DeltaTime;
	else BackDist = temp/6.0*50.0*DeltaTime;
	
	if( temp > 0.0 && BackDist > temp ) BackDist = temp;
	if( temp < 0.0 && BackDist < temp ) BackDist = temp;

	CurZoomingDist += BackDist;
	DesiredZoomingDist = CurZoomingDist;
	
	return true;
}

function bool IsBlockRotation( rotator Rotation, vector TargetLocation, float Dist, int VolumeRadius )
{
	local	vector HitLocation, HitNormal;

	Rotation.Yaw += VolumeRadius;
	if( Trace( HitLocation, HitNormal, TargetLocation - Dist * vector(Rotation), TargetLocation, false ) != None )
	{
		return true;
	}

	Rotation.Yaw -= VolumeRadius*2;
	if( Trace( HitLocation, HitNormal, TargetLocation - Dist * vector(Rotation), TargetLocation, false ) != None )
	{
		return true;
	}

	Rotation.Yaw += VolumeRadius;
	Rotation.Pitch += VolumeRadius;
	if( Trace( HitLocation, HitNormal, TargetLocation - Dist * vector(Rotation), TargetLocation, false ) != None )
	{
		return true;
	}

	Rotation.Pitch -= VolumeRadius*2;
	if( Trace( HitLocation, HitNormal, TargetLocation - Dist * vector(Rotation), TargetLocation, false ) != None )
	{
		return true;
	}

	return false;
}

function CalcVolumeZoomingDistance( float DeltaTime )
{
	local vector HitLocation, HitNormal;
	local float temp, TempDist;
	local vector TempVec;

	if( CurZoomingDist == DesiredZoomingDist ) return;

	temp = DesiredZoomingDist - CurZoomingDist;

	if( -6.0 <= temp && temp < 0.0 ) TempDist = -50.0*DeltaTime;
	else if( 0.0 < temp && temp <= 6.0 ) TempDist = 50.0*DeltaTime;
	else TempDist = temp/6.0*50.0*DeltaTime;
	
	if( temp > 0.0 && TempDist > temp ) TempDist = temp;
	if( temp < 0.0 && TempDist < temp ) TempDist = temp;

	CurZoomingDist += TempDist;

	if( IsBlockRotation( OldCameraRotation, ViewTarget.Location, CurZoomingDist+250, VolumeCameraRadius ) )
	{
		CurZoomingDist -= TempDist;
		return;
	}

	CurVolumeCameraRadius = VolumeCameraRadius;
	TempVec = Viewtarget.Location;
	TempVec.Z += CameraViewHeightAdjust;
	if( Trace( HitLocation, HitNormal, TempVec - (CurZoomingDist + 250) * vector(Rotation), TempVec, false ) != None )
	{
		CurZoomingDist = VSize( HitLocation - TempVec );
		CurZoomingDist -= 250;
	}
}

event PlayerTick( float DeltaTime )
{
	if( bCameraMovingToDefault ) 
	{
		if( bUseDefaultCameraYaw )		bUseDefaultCameraYaw = CalcCameraMovingToDefaultYaw( DeltaTime, SavedViewTargetYaw );
		if( bUseDefaultCameraPitch )	bUseDefaultCameraPitch = CalcCameraMovingToDefaultPitch( DeltaTime, SavedViewTargetPitch );
		if( bUseDefaultCameraDist )		bUseDefaultCameraDist = CalcCameraMovingToDefaultDistance( DeltaTime );

		if( !bUseDefaultCameraYaw && !bUseDefaultCameraPitch && !bUseDefaultCameraDist ) 
		{
			bCameraMovingToDefault = false;
		}
	}
	else if( bUseVolumeCamera ) 
		CalcVolumeZoomingDistance( DeltaTime );
	else if( bCameraWalking )
		CalcCameraWalkingMode( DeltaTime );

	Super.PlayerTick( DeltaTime );
}

function CalcCameraWalkingMode( float DeltaTime )
{
	local int temp, TempYaw, TempPitch;
	local rotator ViewRotation;
	local vector ViewVector;
	
	if( !bCameraWalking ) return;
	if( CameraModeTarget == None ) return;

	ViewVector = CameraModeTarget.Location - Pawn.Location;
	ViewRotation = Vector2Rotator( ViewVector );
	
	if( ( ViewRotation.Yaw - OldCameraRotation.Yaw ) % 65536 != 0 )
	{
		temp = ViewRotation.Yaw - OldCameraRotation.Yaw;
		while( temp > 32768 ) temp -= 65536;
		while( temp < -32767 ) temp += 65536;

		if( -600 <= temp && temp < 0 ) TempYaw = int( -5000.0 * DeltaTime );
		else if( 0 < temp && temp <= 600 ) TempYaw = int( 5000.0 * DeltaTime );
		else TempYaw = int( float(temp) / 6.0 * 50.0 * DeltaTime );

		if( temp > 0 && TempYaw > temp ) TempYaw = temp;
		if( temp < 0 && TempYaw < temp ) TempYaw = temp;

		OldCameraRotation.Yaw += TempYaw;
		while( OldCameraRotation.Yaw > 32768 ) OldCameraRotation.Yaw -= 65536;
		while( OldCameraRotation.Yaw < -32767 ) OldCameraRotation.Yaw += 65536;
	}
	
	if( ( ViewRotation.Pitch - OldCameraRotation.Pitch ) % 65536 != 0 )
	{
		temp = ViewRotation.Pitch - OldCameraRotation.Pitch;
		while( temp > 32768 ) temp -= 65536;
		while( temp < -32767 ) temp += 65536;

		if( -600 <= temp && temp < 0 ) TempPitch = int( -5000.0 * DeltaTime );
		else if( 0 < temp && temp <= 600 ) TempPitch = int( 5000.0 * DeltaTime );
		else TempPitch = int( float(temp) / 6.0 * 50.0 * DeltaTime );

		if( temp > 0 && TempPitch > temp ) TempPitch = temp;
		if( temp < 0 && TempPitch < temp ) TempPitch = temp;

		OldCameraRotation.Pitch += TempPitch;
		while( OldCameraRotation.Pitch > 32768 ) OldCameraRotation.Pitch -= 65536;
		while( OldCameraRotation.Pitch < -32767 ) OldCameraRotation.Pitch += 65536;
		DesiredPitch = OldCameraRotation.Pitch;
	}
}

function CalcVolumeCamera( out vector CameraLocation, out rotator CameraRotation, float ViewDist )
{
	local vector View, HitLocation, HitNormal, TempCameraLocation;
	local rotator TempRotation;

	View = vect(1,0,0) >> CameraRotation;

	TempCameraLocation = CameraLocation - (ViewDist + 30) * vector(CameraRotation);
	if( Trace( HitLocation, HitNormal, TempCameraLocation, CameraLocation, false ) == None )
	{
		CameraLocation -= (ViewDist - 30) * View; 
		return;
	}
	else
	{
		//if( VSize( HitLocation - TempCameraLocation ) < VSize( OldCameraLocation - TempCameraLocation ) )
		//{
			ViewDist = FMin( (CameraLocation - HitLocation) Dot View, ViewDist );
			CameraLocation -= (ViewDist - 30) * View; 
			return;
		//}
	}

	TempRotation = CameraRotation;

	/*for( i=0 ; i<2 ; i++ )
	{
		TempRotation = ( TempRotation + OldCameraRotation ) / 2;
		TempDist = ViewDist - VSize( TempCameraLocation - OldCameraLocation );
		if( Trace( HitLocation, HitNormal, CameraLocation - (TempDist + 30) * vector(TempRotation), CameraLocation, false ) == None )
		{
			View = vect(1,0,0) >> TempRotation;
			CameraLocation -= (TempDist - 30) * View; 
			return;
		}
	}*/

	//ViewDist -= VSize( TempCameraLocation - OldCameraLocation );
	CurZoomingDist -= 5;
	ViewDist -= 5;
	View = vect(1,0,0) >> OldCameraRotation;
	ViewDist = FMin( (CameraLocation - HitLocation) Dot View, ViewDist );
	CameraLocation -= (ViewDist - 30) * View; 
	CameraRotation = OldCameraRotation;
}

function CalcBehindView(out vector CameraLocation, out rotator CameraRotation, float Dist)
{
	local vector View,HitLocation,HitNormal;
	local float ViewDist;

	CameraLocation.Z += CameraViewHeightAdjust;

	if( OldCameraLocation.X == 0 && OldCameraLocation.Y == 0 && OldCameraLocation.Z == 0 )
	{
		OldCameraRotation = Rotation;
	}

	if( OldViewTargetLocation == CameraLocation && ManuallyCameraPitch == 0 && ManuallyCameraYaw == 0 && !bCameraMovingToDefault )
	{
		CameraRotation = OldCameraRotation;
		if(CurZoomingDist == OldZoomingDist) 
		{
			CameraLocation = OldCameraLocation;
			return;
		}
	}
	else
	{
		if( ManuallyCameraYaw != 0 )
		{
			CameraRotation.Yaw = OldCameraRotation.Yaw;
			bCameraMovingToDefault = false;
		}
		else
		{
			if( bCameraMovingToDefault )
			{
				CameraRotation = OldCameraRotation;
				//temp = Rotation.Yaw - CameraRotation.Yaw;
				//while( temp > 32768 ) temp -= 65536;
				//while( temp < -32767 ) temp += 65536;
				//if( CameraRotation.Yaw == Rotation.Yaw || temp == 0) bCameraMovingToDefault = false;
			}
			else
			{
				if( OldCameraLocation.X == 0 && OldCameraLocation.Y == 0 && OldCameraLocation.Z == 0 )
				{
					CameraRotation = Rotation;
				}
				else if( bUseAutoTrackingPawn )
				{
					View = vect(1,1,0)*(CameraLocation-OldCameraLocation);
					CameraRotation = Vector2Rotator(View);
				}
				else
				{
					CameraRotation = OldCameraRotation;
				}
			}
		}
	}

	OldViewTargetLocation = CameraLocation;

	if( bFixView )
	{
		CameraRotation = OldCameraRotation;
		CameraRotation.Yaw += ManuallyCameraYaw;
		CameraRotation.Pitch += ManuallyCameraPitch;
		CameraLocation = OldCameraLocation;
		while( CameraRotation.Yaw > 32768 ) CameraRotation.Yaw = CameraRotation.Yaw - 65536;
		while( CameraRotation.Yaw < -32767 ) CameraRotation.Yaw = CameraRotation.Yaw + 65536;
		while( CameraRotation.Pitch > 32768 ) CameraRotation.Pitch = CameraRotation.Pitch - 65536;
		while( CameraRotation.Pitch < -32767 ) CameraRotation.Pitch = CameraRotation.Pitch + 65536;
		if( CameraRotation.Pitch < -15000) CameraRotation.Pitch = -15000;
		else if( CameraRotation.Pitch > 15000) CameraRotation.Pitch = 15000;
	}
	else
	{
		CameraRotation.Pitch = OldCameraRotation.Pitch;
		CameraRotation.Yaw += ManuallyCameraYaw;
		CameraRotation.Pitch += ManuallyCameraPitch;
		while( CameraRotation.Yaw > 32768 ) CameraRotation.Yaw = CameraRotation.Yaw - 65536;
		while( CameraRotation.Yaw < -32767 ) CameraRotation.Yaw = CameraRotation.Yaw + 65536;
		while( CameraRotation.Pitch > 32768 ) CameraRotation.Pitch = CameraRotation.Pitch - 65536;
		while( CameraRotation.Pitch < -32767 ) CameraRotation.Pitch = CameraRotation.Pitch + 65536;
		if( CameraRotation.Pitch < -15000) CameraRotation.Pitch = -15000;
		else if( CameraRotation.Pitch > 15000) CameraRotation.Pitch = 15000;

		ViewDist = Dist + CurZoomingDist;
		if( bUseVolumeCamera )
			CalcVolumeCamera( CameraLocation, CameraRotation, ViewDist );
		else
		{
			View = vect(1,0,0) >> CameraRotation;
			if( Trace( HitLocation, HitNormal, CameraLocation - (ViewDist + 30) * vector(CameraRotation), CameraLocation, false ) != None )
				ViewDist = FMin( (CameraLocation - HitLocation) Dot View, ViewDist );
			CameraLocation -= (ViewDist - 30) * View; 
		}
	}

	OldCameraLocation = CameraLocation;
	OldCameraRotation = CameraRotation;
	ManuallyCameraPitch = 0;
	ManuallyCameraYaw = 0;
	OldZoomingDist = CurZoomingDist;
}

event PlayerCalcView(out actor ViewActor, out vector CameraLocation, out rotator CameraRotation )
{
	if ( (ViewTarget == None) || ViewTarget.bDeleteMe )
	{
		if ( (Pawn != None) && !Pawn.bDeleteMe )
			SetViewTarget(Pawn);
		else
			SetViewTarget(self);
	}

	if( !bUseVolumeCamera ) CurZoomingDist = DesiredZoomingDist;
	ViewActor = ViewTarget;
	CameraLocation = ViewTarget.Location;

	if ( ViewTarget == Pawn )
	{
		if( bBehindView ) //up and behind
			CalcBehindView(CameraLocation, CameraRotation, 250);
		else
			CalcFirstPersonView( CameraLocation, CameraRotation );
		return;
	}
	if ( ViewTarget == self )
	{
		CameraRotation = Rotation;
		return;
	}
}

//#ifdef	__L2	Hunter
function ViewPlayer()
{
	SetViewTarget(Pawn);

	bBehindView = true;
	if ( bBehindView )
	{
		ViewTarget.BecomeViewTarget();
	}
}
//#endif

function ClientRestart()
{
	if ( Pawn == None )
	{
		GotoState('WaitingForPawn');
		return;
	}
	Pawn.ClientRestart();
	SetViewTarget(Pawn);
//#ifdef	__L2	Hunter
	ViewPlayer();
//#else
	//CheatManager.ViewPlayer("");
//#endif
	EnterStartState();	
}

state PlayerSpidering
{
	// if spider mode, update rotation based on floor					
	/*function UpdateRotation(float DeltaTime, float maxPitch)
	{
		local rotator TempRot, ViewRotation;
		local vector MyFloor, CrossDir, FwdDir, OldFwdDir, OldX, RealFloor;

		if ( bInterpolating || Pawn.bInterpolating )
		{
			ViewShake(deltaTime);
			return;
		}

		TurnTarget = None;
		bRotateToDesired = false;
		bSetTurnRot = false;

		if ( (Pawn.Base == None) || (Pawn.Floor == vect(0,0,0)) )
			MyFloor = vect(0,0,1);
		else
			MyFloor = Pawn.Floor;

		if ( MyFloor != OldFloor )
		{
			// smoothly change floor
			RealFloor = MyFloor;
			MyFloor = Normal(6*DeltaTime * MyFloor + (1 - 6*DeltaTime) * OldFloor);
			if ( (RealFloor Dot MyFloor) > 0.999 )
				MyFloor = RealFloor;

			// translate view direction
			CrossDir = Normal(RealFloor Cross OldFloor);
			FwdDir = CrossDir Cross MyFloor;
			OldFwdDir = CrossDir Cross OldFloor;
			ViewX = MyFloor * (OldFloor Dot ViewX) 
						+ CrossDir * (CrossDir Dot ViewX) 
						+ FwdDir * (OldFwdDir Dot ViewX);
			ViewX = Normal(ViewX);
			
			ViewZ = MyFloor * (OldFloor Dot ViewZ) 
						+ CrossDir * (CrossDir Dot ViewZ) 
						+ FwdDir * (OldFwdDir Dot ViewZ);
			ViewZ = Normal(ViewZ);
			OldFloor = MyFloor;  
			ViewY = Normal(MyFloor Cross ViewX); 
		}

		if ( (aTurn != 0) || (aLookUp != 0) )
		{
			// adjust Yaw based on aTurn
			if ( aTurn != 0 )
				ViewX = Normal(ViewX + 2 * ViewY * Sin(0.0005*DeltaTime*aTurn));

			// adjust Pitch based on aLookUp
			if ( aLookUp != 0 )
			{
				OldX = ViewX;
				ViewX = Normal(ViewX + 2 * ViewZ * Sin(0.0005*DeltaTime*aLookUp));
				ViewZ = Normal(ViewX Cross ViewY);

				// bound max pitch
				if ( (ViewZ Dot MyFloor) < 0.707   )
				{
					OldX = Normal(OldX - MyFloor * (MyFloor Dot OldX));
					if ( (ViewX Dot MyFloor) > 0)
						ViewX = Normal(OldX + MyFloor);
					else
						ViewX = Normal(OldX - MyFloor);

					ViewZ = Normal(ViewX Cross ViewY);
				}
			}
			
			// calculate new Y axis
			ViewY = Normal(MyFloor Cross ViewX);
		}
		ViewRotation =  OrthoRotation(ViewX,ViewY,ViewZ);
		SetRotation(ViewRotation);
		ViewShake(deltaTime);
		ViewFlash(deltaTime);
		Pawn.FaceRotation(ViewRotation, deltaTime);
	}*/
}

state Spectating
{
	// Return to spectator's own camera.
	exec function AltFire( optional float F )
	{
//__L2 by Hunter
		//bBehindView = false;
		//SetViewtarget(self);
//by Hunter End
		ClientMessage(OwnCamera, 'Event');
	}
}

//__L2 by nonblock
simulated event LostChild( Actor Other )
{
	if(AirEffect == Other)
		AirEffect=None;
	Super.LostChild( Other );
}

simulated event ClearL2Game()
{
	if(AirEffect!=None)
	{
		AirEffect.NDestroy();
		AirEffect=None;
	}
	Super.ClearL2Game();
}
// end. by nonblock


