#ifndef GUARD_ICON_H
#define GUARD_ICON_H
#include "global.h"
#define MAX_ICON_COUNT 206

typedef struct IconStruct {
    u8 Sheet; // What sheet the icon belong too
    u8 Index;
} IconStruct;

#define EMPTY_ICON ((IconStruct) {.Sheet = 0xFF, .Index = 0xFF})

enum icon_sheet_idx {
    ICON_SHEET_VANILLA,
    ICON_SHEET_AFFIN,
    ICON_SHEET_MOUNT,
    ICON_SHEET_WTYPE,
    ICON_SHEET_COMBATART,
    ICON_SHEET_SKILL,
    ICON_SHEET_SKILL1,
    ICON_SHEET_SKILL2,
    ICON_SHEET_SKILL3,

    ICON_SHEET_AMT = 16
};

#define AFFIN_ICON(affin) ((IconStruct) { .Sheet = ICON_SHEET_AFFIN, .Index = affin })
#define MOUNT_ICON(mount) ((IconStruct) { .Sheet = ICON_SHEET_MOUNT, .Index = mount })
#define WTYPE_ICON(wtype) ((IconStruct) { .Sheet = ICON_SHEET_WTYPE, .Index = wtype })
#define ITEM_ICON(item)   ((IconStruct) { .Sheet = ICON_SHEET_VANILLA, .Index = item })
#define SKILL_ICON(sid)   ((IconStruct) { .Sheet = ICON_SHEET_SKILL, .Index = sid })

#define MAX_SIMULTANEOUS_ICONS 32

typedef const u8* (*IconGetterFunc)(const u8 index);
extern const IconGetterFunc IconGetters[];

const u8 *GetIconGfx(struct IconStruct icon);
const u8 *IconGetterVanilla(const u8 index);
const u8 *GetAffinIcon(const u8 index);
const u8 *GetMountIcon(const u8 index);
const u8 *GetWTypeIcon(const u8 index);
const u8 *GetSkillIcon(const u8 index);

u8 extern const *gAffinIcons[0x100];
u8 extern const *gMountIcons[0x100];
u8 extern const *gWTypeIcons[0x100];

void ResetIconGraphics();
void LoadIconPalettes(u32 Dest);
void LoadIconPalette(u32 Index, u32 Dest);
int sub_80035EC();
u16 GetIconGfxTileIndex(u32 Index);
u16 GetIconTileIndex(IconStruct Index); // NONMATCHING
void DrawIcon(u16* BgOut,IconStruct icon, int OamPalBase);
void ClearIconGfx(u32 Index);
void LoadIconObjectGraphics(IconStruct icon, int b);

extern const u16 item_icon_palette[2][16]; // Item Icon Palette
extern const u8 item_icon_tiles[MAX_ICON_COUNT][0x80]; // Item Icon GFX

#endif  // GUARD_ICON_H
