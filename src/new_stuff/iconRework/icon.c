#include "global.h"
#include "icon.h"
#include "hardware.h"

#define MAX_ICON_COUNT 224
#define MAX_ICON_GFX_COUNT 32

//EWRAM_DATA static IconStruct DrawnIconLookupTable[MAX_ICON_COUNT] = {0};
EWRAM_DATA static IconStruct DrawnIconLookupTable[MAX_ICON_GFX_COUNT] = {0};

const u8 *GetIconGfx(IconStruct icon)
{
    if (icon.Sheet < ICON_SHEET_AMT)
        return IconGetters[icon.Sheet](icon.Index);

    return NULL;
}

int GetIconUsedSlot(u8 sheet, u8 index)
{
    int i;

    for (i = 0; i < MAX_SIMULTANEOUS_ICONS; i++)
        if (sheet == DrawnIconLookupTable[i].Sheet && index == DrawnIconLookupTable[i].Index)
            return i + 1;

    return 0;
}

int GetIconNewSlot(u8 sheet, u8 index)
{
    int i;

    for (i = 0; i < MAX_SIMULTANEOUS_ICONS; i++) {
        if ((u8)0xFF == DrawnIconLookupTable[i].Index) {
            DrawnIconLookupTable[i].Sheet = sheet;
            DrawnIconLookupTable[i].Index = index;
            return i + 1;
        }
    }

    return 0;
}

void ResetIconGraphics()
{
    CpuFill16(-1, &DrawnIconLookupTable, sizeof(DrawnIconLookupTable));
}

void LoadIconPalettes(u32 Dest)
{
    ApplyPalettes(item_icon_palette[0], Dest, 2);
}

void LoadIconPalette(u32 Index, u32 Dest)
{
    ApplyPalette(item_icon_palette[Index], Dest);
}

u16 GetIconGfxTileIndex(u32 Index)
{
    return 0x300 - Index * 4;
}

u16  GetIconTileIndex(IconStruct icon)
{
    int slot, tile;
    const u8 *src;
    u8 *dst;

    slot = GetIconUsedSlot(icon.Sheet,icon.Index);
    if (slot != 0)
        return GetIconGfxTileIndex(slot);

    /* Register new icon */
    slot = GetIconNewSlot(icon.Sheet,icon.Index);
    tile = GetIconGfxTileIndex(slot);

    src = GetIconGfx(icon);
    dst = (void *)(BG_VRAM + tile * CHR_SIZE);

    if (src)
        RegisterDataMove(src, dst, CHR_SIZE * 4);
    else
        RegisterFillTile(0,   dst, CHR_SIZE * 4);

    return tile;
}

void DrawIcon(u16* BgOut,IconStruct icon, int OamPalBase)
{
    if (icon.Index == 0xFF ) {
        BgOut[0]  = 0;
        BgOut[1]  = 0;
        BgOut[32] = 0;
        BgOut[33] = 0;
    } else {
        u16 Tile = GetIconTileIndex(icon) + OamPalBase;

        BgOut[0]  = Tile++;
        BgOut[1]  = Tile++;
        BgOut[32] = Tile++;
        BgOut[33] = Tile;
    }
}

void ClearIconGfx(u32 Index)
{
    int i = 0;
    for (i = 0; i < MAX_SIMULTANEOUS_ICONS; i++) {
        if(DrawnIconLookupTable[i].Index == Index)
        {
            DrawnIconLookupTable[i].Index = 0xFF;
            DrawnIconLookupTable[i].Sheet = 0xFF;
        }
    }
}

void LoadIconObjectGraphics(IconStruct icon, int chr)
{
    const u8 *src = GetIconGfx(icon);
    u8 *dst = OBJ_VRAM0 + CHR_SIZE * (chr & 0x3FF);

    if (!src) {
        RegisterFillTile(0, dst,         CHR_SIZE * 2);
        RegisterFillTile(0, dst + 0x400, CHR_SIZE * 2);
        return;
    }

    RegisterDataMove(src,                dst,         CHR_SIZE * 2);
    RegisterDataMove(src + CHR_SIZE * 2, dst + 0x400, CHR_SIZE * 2);
}