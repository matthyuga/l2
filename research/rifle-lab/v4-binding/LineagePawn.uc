//=============================================================================
// LineagePawn:  base class of Lineage pawns which use MoCap animation
//=============================================================================

class LineagePawn extends Pawn;



// #exec OBJ LOAD FILE=..\Animations\LineageWarriors.ukx PACKAGE=LineageWarriors
// #exec OBJ LOAD FILE=..\Animations\LineageNpcs.ukx PACKAGE=LineageNpcs
// #exec OBJ LOAD FILE=..\Animations\LineageMonsters.ukx PACKAGE=LineageMonsters
// #exec OBJ LOAD FILE=..\Animations\LineageMonsters2.ukx PACKAGE=LineageMonsters2
// #exec OBJ LOAD FILE=..\Animations\LineageWeapons.ukx PACKAGE=LineageWeapons


//==============================================================================
//UnrealPawn.uc
simulated event SetAnimAction(name NewAction)
{
    AnimAction = NewAction;
	PlayAnim(AnimAction);
}

function String GetDebugName()
{
	return GetItemName(string(self));
}

function SetMovementPhysics()
{
	if (Physics == PHYS_Falling)
		return;
	if ( PhysicsVolume.bWaterVolume )
		SetPhysics(PHYS_Swimming);
	else
		SetPhysics(PHYS_Walking); 
}

//==============================================================================
//WarfarePawn.uc
simulated event Destroyed()
{
// #ifdef __L2 // by zodiac
	if ( Shadow1 != None ) {
		Shadow1.DetachProjector(true);
		Shadow1.NDestroy();
	}
// #else
// if ( Shadow != None )
//	Shadow.Destroy();
// #endif // zodiac
// #ifdef __L2 // kurt
	if ( Mark != None ) {
		Mark.DetachProjector(true);
		Mark.NDestroy();
	}
// #end

	Super.Destroyed();
}

simulated function DisplayDebug(Canvas Canvas, out float YL, out float YPos)
{
	Super.DisplayDebug(Canvas, YL, YPos);

	Canvas.SetDrawColor(255,255,255);

	YPos += YL;
}

function float MovetoZero(float step, float Value)
{
	if (Value<0)
	{
		Value += Step;
		if (Value<0)
			return Value;
		else
			return 0;
	}
	else if (Value>0)
	{
		Value -= Step;
		if (Value>0)
			return Value;
		else
			return 0;
	}
}	

function PostBeginPlay()
{
	Super.PostBeginPlay();

//#ifdef __L2 //kurt
	//Mark = Spawn(class'MarkProjector',Self,'',Location);
//#endif
	TurnLeftAnim = GetWalkAnimName();
	TurnRightAnim = GetWalkAnimName();
	MovementAnims[0] = GetCurMoveAnimName();
	MovementAnims[1] = GetCurMoveAnimName();
	MovementAnims[2] = GetCurMoveAnimName();
	MovementAnims[3] = GetCurMoveAnimName();
	//kurt
	PlayAnim(GetCurWaitAnimName());
	if(bActorShadows)
	{
		Shadow1 = Spawn(class'ShadowProjector',Self,'',Location);
		Shadow1.ShadowActor = self;
		Shadow1.LightDirection = Normal(vect(1,1,5));
//#ifdef __L2 zodiac
		Shadow1.LightDistance = 380*4;
		Shadow1.MaxTraceDistance = 380*4;
//#else
		//Shadow1.LightDistance = 380*4;
		//Shadow1.MaxTraceDistance = 350*4;
//#endif
		Shadow1.InitShadow();
		Shadow1.UpdateShadow();
	}

}

// Notify called when ready to land (should loop)
function CheckLanding()
{
	if ( Physics == PHYS_Falling )
	{
		// stop animating, haven't landed yet
		TweenAnim('Land', 9000.0);
	}
}

//-----------------------------------------------------------------------------
// Animation functions

simulated event ChangeAnimation()
{
	if ( (Controller != None) && Controller.bControlAnimations )
		return;
	// player animation - set up new idle and moving animations
	PlayWaiting();
	PlayMoving();
}

simulated event PlayFalling()
{
	local name OldAnim;
	local float frame,rate;

	GetAnimParams(0,OldAnim,frame,rate);

	if ( (OldAnim=='Jump_run') || (OldAnim=='Jump_stand') )
		return;

	PlayJump();	
}

simulated function PlayWaiting()
{
	if ( KVehicle(Base) != None )
		AnimateRiding();
	else if ( Physics == PHYS_Swimming )
		AnimateTreading();
	else if ( Physics == PHYS_Flying )
		AnimateFlying();
	else if ( Physics == PHYS_Ladder )
		AnimateStoppedOnLadder();
	else if ( Physics == PHYS_Falling )
		PlayFalling();
	else if ( bIsCrouched )
		AnimateCrouching();
	else
		AnimateStanding();
}

simulated function PlayMoving()
{
	if ( (Physics == PHYS_None) 
		|| ((Controller != None) && Controller.bPreparingMove) )
	{
		// bot is preparing move - not really moving 
		PlayWaiting();
		return;
	}
	if ( Physics == PHYS_Walking )
	{
		if ( bIsCrouched )
			AnimateCrouchWalking();
		else if ( bIsWalking )
			AnimateWalking();
		else
			AnimateRunning();
	}
	else if ( (Physics == PHYS_Swimming)
		|| ((Physics == PHYS_Falling) && IsPlayingSwimming() && TouchingWaterVolume()) )
		AnimateSwimming();
	else if ( Physics == PHYS_Ladder )
		AnimateClimbing();
	else if ( Physics == PHYS_Flying )
		AnimateFlying();
	else
	{
		if ( bIsCrouched )
			AnimateCrouchWalking();
		else if ( bIsWalking )
			AnimateWalking();
		else
			AnimateRunning();
	}
}

/* LoopIfNeeded()
play looping idle animation only if not already animating
*/
simulated function LoopIfNeeded(name NewAnim, float NewRate, float BlendIn)
{
	local name OldAnim;
	local float frame,rate;

	GetAnimParams(0,OldAnim,frame,rate);

	// FIXME - get tween time from anim
	if ( (NewAnim != OldAnim) || (NewRate != Rate) || !IsAnimating(0) )
		LoopAnim(NewAnim, NewRate, BlendIn);
	else
		LoopAnim(NewAnim, NewRate);
}
//************************************************************************************
// Private animation functions

// Current assumptions
// 
// all swimming and treading water anims should belong to the group SWIMMING
// all running anims should belong to the group RUNNING

simulated function bool IsPlayingSwimming()
{
	return AnimIsInGroup(0,'SWIMMING');
}

/* AnimateSwimming()
Moving through water - check acceleration for direction
*/
simulated function AnimateSwimming()
{
	MovementAnims[0] = 'Swim';
	MovementAnims[1] = 'Swim';
	MovementAnims[2] = 'Swim';
	MovementAnims[3] = 'Swim';
}

/* AnimateTreading()
Still in water
*/
simulated function AnimateTreading()
{
	MovementAnims[0] = 'Swim';
	MovementAnims[1] = 'Swim';
	MovementAnims[2] = 'Swim';
	MovementAnims[3] = 'Swim';
}

/* AnimateClimbing()
climbing
*/
simulated function AnimateClimbing()
{
	local name NewAnim;
	local int i;

	if ( (OnLadder == None) || (OnLadder.ClimbingAnimation == '') )
		NewAnim = 'Ladder_Climb'; 
	else
		NewAnim = OnLadder.ClimbingAnimation;
	for ( i=0; i<4; i++ )
		MovementAnims[i] = NewAnim;
	TurnLeftAnim = NewAnim;
	TurnRightAnim = NewAnim;
}

simulated function AnimateStoppedOnLadder()
{
	local name NewAnim;

	if ( (OnLadder == None) || (OnLadder.ClimbingAnimation == '') )
		NewAnim = 'Ladder_Climb'; 
	else
		NewAnim = OnLadder.ClimbingAnimation;
	TweenAnim(NewAnim, 1.0); // FIXME TEMP - need paused on ladder animation
}

/* AnimateFlying()
flying - not used in Warfare, so don't need real animation
*/
simulated function AnimateFlying()
{
	AnimateSwimming();
}

simulated function AnimateRiding()
{
}

simulated function AnimateCrouching()
{
	LoopIfNeeded('Crouch',1.0,0.25);
}
	
//==============================================================================
//LineagePawn.uc
function name GetCurMoveAnimName()
{
	if( controller != None )
	{
		if( controller.MoveType == PMT_SLOW )
			return GetWalkAnimName(); 
		else if( controller.MoveType == PMT_FAST )
			return GetRunAnimName(); 
	}
	return GetRunAnimName();
}

function name GetCurWaitAnimName()
{
	if( controller != None )
	{
		if( Controller.bDead ) return GetDeathWaitAnimName();
		if( controller.WaitType == STP_SIT ) return GetSitWaitAnimName(); 
		if( controller.WaitType == STP_FAKE_DEAD ) return GetDeathWaitAnimName(); 
		if( Controller.bAutoAttacking ) 
		{
			if( Physics == PHYS_Swimming && SwimAttackWaitAnimName[CurWeaponType] != 'None' )
				return SwimAttackWaitAnimName[CurWeaponType];
			else
				return GetAtkWaitAnimName();
		}
		if( controller.WaitType == STP_STAND ) 
		{
			if ( Physics == PHYS_Swimming && SwimWaitAnimName[CurWeaponType] != 'None' )
				return SwimWaitAnimName[CurWeaponType];
			else
				return GetWaitAnimName();
		}
	}
	return GetWaitAnimName();
}

simulated function AnimateCrouchWalking()
{
	TurnLeftAnim = GetWalkAnimName();
	TurnRightAnim = GetWalkAnimName();
	MovementAnims[0] = GetWalkAnimName();
	MovementAnims[1] = GetWalkAnimName();
	MovementAnims[2] = GetWalkAnimName();
	MovementAnims[3] = GetWalkAnimName();

//#ifdef	__L2	Hunter
	//LoopIfNeeded(GetWalkAnimName(), 1.0, 0.1);
//#endif
}

simulated function AnimateWalking()
{
	TurnLeftAnim = GetWalkAnimName();
	TurnRightAnim = GetWalkAnimName();
	MovementAnims[0] = GetWalkAnimName();
	MovementAnims[1] = GetWalkAnimName();
	MovementAnims[2] = GetWalkAnimName();
	MovementAnims[3] = GetWalkAnimName();

//#ifdef	__L2	Hunter
	//LoopIfNeeded(GetWalkAnimName(), 1.0, 0.1);
//#endif
}

simulated function AnimateStanding()
{
   	if ( (PlayerController(Controller) != None) && PlayerController(Controller).bIsTyping )
	{
		// FIXME - play chatting animation
		return;
	}
 	LoopIfNeeded(GetCurWaitAnimName(), 1.0, 0.2);

}

simulated function AnimateRunning()
{
	TurnLeftAnim = GetWalkAnimName();
	TurnRightAnim = GetWalkAnimName();
	MovementAnims[0] = GetCurMoveAnimName();
	MovementAnims[1] = GetCurMoveAnimName();
	MovementAnims[2] = GetCurMoveAnimName();
	MovementAnims[3] = GetCurMoveAnimName();

//#ifdef	__L2	Hunter
	//LoopIfNeeded(GetCurMoveAnimName(), 1.0, 0.1);
//#endif
}

	
