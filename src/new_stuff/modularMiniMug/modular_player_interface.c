#include "global.h"

#include "player_interface.h"
#include "fontgrp.h"
#include "bmunit.h"
#include "hardware.h"
#include "bmmap.h"
#include "ctc.h"
#include "bmtrick.h"
#include "icon.h"
#include "uiutils.h"
#include "uichapterstatus.h"
#include "chapterdata.h"
#include "face.h"
#include "bm.h"
#include "prepscreen.h"
#include "statscreen.h"
#include "bmlib.h"
#include "worldmap.h"
#include "bmitem.h"

#include "constants/event-flags.h"
#include "constants/msg.h"
#include "constants/terrains.h"
//Size variable for sliding in animation
s8 CONST_DATA sMMBSlideInWidthLut[4] =
{
    5, 9, 13, MiniMugWidth
};
//Size variable for sliding out animation
s8 CONST_DATA sMMBSlideOutWidthLut[3] =
{
    15, 7, 0
};

void MMB_Loop_SlideIn(struct PlayerInterfaceProc * proc)
{
    int tmIndex;
    int width;

    int y = sPlayerInterfaceConfigLut[proc->cursorQuadrant].yMinimug < 0 ? 0 : 14;

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        tmIndex = TILEMAP_INDEX(0, y);

        TileMap_FillRect(gBG0TilemapBuffer + tmIndex, MiniMugWidth, MiniMugHeight, 0);
        TileMap_FillRect(gBG1TilemapBuffer + tmIndex, MiniMugWidth, MiniMugHeight, 0);
    }
    else
    {
        tmIndex = TILEMAP_INDEX(0, y);

        TileMap_FillRect(gBG0TilemapBuffer + TILEMAP_INDEX(MiniMugWidth, 0) + tmIndex, MiniMugWidth, MiniMugHeight, 0);
        TileMap_FillRect(gBG1TilemapBuffer + TILEMAP_INDEX(MiniMugWidth, 0) + tmIndex, MiniMugWidth, MiniMugHeight, 0);
    }

    tmIndex = TILEMAP_INDEX(0, y);

    BG_EnableSyncByMask(BG0_SYNC_BIT | BG1_SYNC_BIT);

    width = sMMBSlideInWidthLut[proc->showHideClock];

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        TileMap_CopyRect(gUiTmScratchA + (MiniMugWidth - width), gBG0TilemapBuffer + tmIndex, width, MiniMugHeight);
        TileMap_CopyRect(gUiTmScratchB + (MiniMugWidth - width), gBG1TilemapBuffer + tmIndex, width, MiniMugHeight);
    }
    else
    {
        TileMap_CopyRect(gUiTmScratchA, gBG0TilemapBuffer + TILEMAP_INDEX(34 - width, y), width, MiniMugHeight);
        TileMap_CopyRect(gUiTmScratchB, gBG1TilemapBuffer + TILEMAP_INDEX(34 - width, y), width, MiniMugHeight);
    }

    proc->showHideClock++;

    if (proc->showHideClock == 4)
    {
        proc->hideContents = false;
        proc->showHideClock = 0;

        Proc_Break(proc);

        UnitMapUiUpdate(proc, GetUnit(gBmMapUnit[gBmSt.playerCursor.y][gBmSt.playerCursor.x]));
    }

    return;
}

void MMB_Loop_SlideOut(struct PlayerInterfaceProc * proc)
{
    int tmIndex;
    int width;

    int y = sPlayerInterfaceConfigLut[proc->cursorQuadrant].yMinimug < 0 ? 0 : 14;

    proc->hideContents = true;

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        tmIndex = TILEMAP_INDEX(0, y);

        TileMap_FillRect(gBG0TilemapBuffer + tmIndex, MiniMugWidth, MiniMugHeight, 0);
        TileMap_FillRect(gBG1TilemapBuffer + tmIndex, MiniMugWidth, MiniMugHeight, 0);
    }
    else
    {
        tmIndex = TILEMAP_INDEX(0, y);

        TileMap_FillRect(gBG0TilemapBuffer + TILEMAP_INDEX(MiniMugWidth, 0) + tmIndex, MiniMugWidth, MiniMugHeight, 0);
        TileMap_FillRect(gBG1TilemapBuffer + TILEMAP_INDEX(MiniMugWidth, 0) + tmIndex, MiniMugWidth, MiniMugHeight, 0);
    }

    tmIndex = TILEMAP_INDEX(0, y);

    BG_EnableSyncByMask(BG0_SYNC_BIT | BG1_SYNC_BIT);

    width = sMMBSlideOutWidthLut[proc->showHideClock];

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        TileMap_CopyRect(gUiTmScratchA + (MiniMugWidth - width), gBG0TilemapBuffer + tmIndex, width, MiniMugHeight);
        TileMap_CopyRect(gUiTmScratchB + (MiniMugWidth - width), gBG1TilemapBuffer + tmIndex, width, MiniMugHeight);
    }
    else
    {
        TileMap_CopyRect(gUiTmScratchA, gBG0TilemapBuffer + TILEMAP_INDEX(34 - width, y), width, MiniMugHeight);
        TileMap_CopyRect(gUiTmScratchB, gBG1TilemapBuffer + TILEMAP_INDEX(34 - width, y), width, MiniMugHeight);
    }

    proc->showHideClock++;

    if (proc->showHideClock == 3)
    {
        proc->isRetracting = false;
        proc->showHideClock = 0;
        proc->windowQuadrant = -1;

        Proc_Break(proc);
    }

    return;
}

void PutUnitMapUiWindow(struct PlayerInterfaceProc * proc)
{
    int x;
    int y;

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        x = 0;
    }
    else
    {
        x = 18;
    }

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].yMinimug < 0)
    {
        y = 0;
    }
    else
    {
        y = 14;
    }

    TileMap_CopyRect(gUiTmScratchA, gBG0TilemapBuffer + TILEMAP_INDEX(x, y), MiniMugWidth, 6);
    BG_EnableSyncByMask(BG0_SYNC_BIT | BG1_SYNC_BIT);

    return;
}

void UnitMapUiUpdate(struct PlayerInterfaceProc * proc, struct Unit * unit)
{
    s16 frameCount = proc->unitClock;

    if (unit->statusIndex == UNIT_STATUS_RECOVER)
    {
        frameCount = 0;
    }

    if ((frameCount & 63) == 0)
    {
        if ((frameCount & 64) != 0)
        {
            PutUnitMapUiStatus(proc->statusTm, unit);
            BG_EnableSyncByMask(BG0_SYNC_BIT);
        }
        else
        {
            if (GetUnitCurrentHp(unit) >= 100)
            {
                StoreNumberStringOrDashesToSmallBuffer(0xFF);
            }
            else
            {
                StoreNumberStringOrDashesToSmallBuffer(GetUnitCurrentHp(unit));
            }

            proc->hpCurHi = gNumberStr[6] - '0';
            proc->hpCurLo = gNumberStr[7] - '0';

            if (GetUnitMaxHp(unit) >= 100)
            {
                StoreNumberStringOrDashesToSmallBuffer(0xFF);
            }
            else
            {
                StoreNumberStringOrDashesToSmallBuffer(GetUnitMaxHp(unit));
            }

            proc->hpMaxHi = gNumberStr[6] - '0';
            proc->hpMaxLo = gNumberStr[7] - '0';

            ClearUnitMapUiStatus(proc, proc->statusTm, unit);
            BG_EnableSyncByMask(BG0_SYNC_BIT);
        }
    }

    if ((proc->hideContents == false) && ((frameCount & 64) == 0 || (unit->statusIndex == UNIT_STATUS_NONE)))
    {
        int xHPDigits;
        int yHPDigits;

        int xHPDigit1;

        xHPDigits = (proc->xHp+xHPpos) * 8;
        xHPDigit1 = xHPDigits + 17;

        yHPDigits = (proc->yHp+yHPpos) * 8;

        if (proc->hpCurHi != (u8)(' ' - '0'))
        {
            CallARM_PushToSecondaryOAM(xHPDigit1, yHPDigits, gObject_8x8, proc->hpCurHi + OAM2_CHR(0x2E0) + OAM2_PAL(8));
        }

        CallARM_PushToSecondaryOAM(xHPDigits + 24, yHPDigits, gObject_8x8, proc->hpCurLo + OAM2_CHR(0x2E0) + OAM2_PAL(8));

        if (proc->hpMaxHi != (u8)(' ' - '0'))
        {
            CallARM_PushToSecondaryOAM(
                xHPDigits + 41, yHPDigits, gObject_8x8, proc->hpMaxHi + OAM2_CHR(0x2E0) + OAM2_PAL(8));
        }

        CallARM_PushToSecondaryOAM(xHPDigits + 48, yHPDigits, gObject_8x8, proc->hpMaxLo + OAM2_CHR(0x2E0) + OAM2_PAL(8));
    }
    UnitNewMiniMugInfo(proc, unit,unit->level,xLVpos,yLVpos);
    UnitNewMiniMugInfo(proc, unit,unit->exp,xEXPpos,yEXPpos);
    BattleGenerateUiStats(unit,GetUnitEquippedWeaponSlot(unit));
    UnitNewMiniMugInfo(proc, unit,gBattleActor.battleAttack,xATKpos,yATKpos);
    UnitNewMiniMugInfo(proc, unit,gBattleActor.battleSpeed,xASpos,yASpos);
    UnitNewMiniMugInfo(proc, unit,GetUnitDefense(unit),xDEFpos,yDEFpos);
    UnitNewMiniMugInfo(proc, unit,GetUnitResistance(unit),xRESpos,yRESpos);
    //Equiped Item Icon is draw as a SPRITE at the given coord
    {
    int xItemCoord, yItemCoord;
    xItemCoord = (proc->xHp + xItemIcon) * 8;
    yItemCoord = (proc->yHp + yItemIcon) * 8;
    LoadIconPalette(0, 0x15); //Loading the item icon pal
        LoadIconObjectGraphics(ITEM_ICON(GetItemIconId(GetUnitEquippedWeapon(unit))),0xF0); //loading the sprite in sprite memory
        CallARM_PushToSecondaryOAM(xItemCoord, yItemCoord, gObject_16x16, OAM2_CHR(0xF0) + OAM2_PAL(0x15));
    }
    return;
}

//Draw the given number at the given coord
void UnitNewMiniMugInfo(struct PlayerInterfaceProc * proc, struct Unit * unit,s8 numbertoinsert,int xDigits,int yDigits)
{
    u8 numberHi, numberLow;
    int xCoord, yCoord;
    StoreNumberStringOrDashesToSmallBuffer(numbertoinsert);
    numberHi = gNumberStr[6] - '0';
    numberLow = gNumberStr[7] - '0';
    xCoord = (proc->xHp + xDigits) * 8+1;
    yCoord = (proc->yHp + yDigits) * 8;
    if (numberHi != (u8)(' ' - '0'))
    {
        CallARM_PushToSecondaryOAM(xCoord, yCoord, gObject_8x8, numberHi + OAM2_CHR(0x2E0) + OAM2_PAL(8));
    }
    CallARM_PushToSecondaryOAM(xCoord + 8, yCoord, gObject_8x8, numberLow + OAM2_CHR(0x2E0) + OAM2_PAL(8));
    return;
}


void DrawUnitMapUi(struct PlayerInterfaceProc * proc, struct Unit * unit)
{
    char * str;
    int faceId;

    CpuFastFill(0, gUiTmScratchA, 6 * CHR_SIZE * sizeof(u16));
    CallARM_FillTileRect(gUiTmScratchA, gNewTSA_MinimugAttrBox, TILEREF(0x100, 1));

    str = GetStringFromIndex(unit->pCharacterData->nameTextId);
    ClearText(proc->texts);
    Text_SetParams(proc->texts, 0, TEXT_COLOR_SYSTEM_BLACK);
    Text_DrawString(proc->texts, str);
    PutText(proc->texts, gUiTmScratchA + TILEMAP_INDEX(5, 3));

    faceId = GetUnitMiniPortraitId(unit);

    if (unit->state & US_BIT23)
    {
        faceId = faceId + 1;
    }
    PutFaceChibi(faceId, gUiTmScratchA + TILEMAP_INDEX(1, 1), 0xF0, 4, 0);

    proc->statusTm = gUiTmScratchA + TILEMAP_INDEX(5,1);
    proc->unitClock = 0;

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].xMinimug < 0)
    {
        proc->xHp = 2;
    }
    else
    {
        proc->xHp = 20;
    }

    if (sPlayerInterfaceConfigLut[proc->cursorQuadrant].yMinimug < 0)
    {
        proc->yHp = 0;
    }
    else
    {
        proc->yHp = 14;
    }

    UnitMapUiUpdate(proc, unit);

    CallARM_FillTileRect(gUiTmScratchB, gNewTSA_MinimugBox, TILEREF(0x0, 3));
    ApplyUnitMapUiFramePal(UNIT_FACTION(unit), 3);

    return;
}