#include "global.h"
#include "anime.h"
#include "gba_sprites.h"

u16 Img_LvupApfx[] = INCBIN_U16("graphics/lvup/LvupAp.4bpp.lz");
u16 Pal_LvupApfx[] = INCBIN_U16("graphics/lvup/LvupAp.gbapal");
u16 gUnknown_085bb2fc[] = INCBIN_U16("graphics/unsorted/gUnknown_085bb2fc.bin");
u8 Img_ArenaBattleBg[] = INCBIN_U8("graphics/unsorted/Img_ArenaBattleBg.4bpp.lz");
u8 Tsa_ArenaBattleBg[] = INCBIN_U8("graphics/unsorted/Tsa_ArenaBattleBg.bin.lz");
u16 Pal_ArenaBattleBg_A[] = INCBIN_U16("graphics/unsorted/Pal_ArenaBattleBg_A.gbapal");
u16 Pal_ArenaBattleBg_B[] = INCBIN_U16("graphics/unsorted/Pal_ArenaBattleBg_B.gbapal");
u16 Pal_ArenaBattleBg_C[] = INCBIN_U16("graphics/unsorted/Pal_ArenaBattleBg_C.gbapal");
u16 gUnknown_085bf114[] = INCBIN_U16("graphics/unsorted/gUnknown_085bf114.bin");
u16 Img1_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img1_EfxLvupBG.bin.lz");
u16 Img2_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img2_EfxLvupBG.bin.lz");
u16 Img3_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img3_EfxLvupBG.bin.lz");
u16 Img4_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img4_EfxLvupBG.bin.lz");
u16 Img5_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img5_EfxLvupBG.bin.lz");
u16 Img6_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img6_EfxLvupBG.bin.lz");
u16 Img7_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Img7_EfxLvupBG.bin.lz");
u16 Pal_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Pal_EfxLvupBG.gbapal");
u16 Tsa1_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa1_EfxLvupBG.bin.lz");
u16 Tsa2_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa2_EfxLvupBG.bin.lz");
u16 Tsa3_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa3_EfxLvupBG.bin.lz");
u16 Tsa4_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa4_EfxLvupBG.bin.lz");
u16 Tsa5_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa5_EfxLvupBG.bin.lz");
u16 Tsa6_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa6_EfxLvupBG.bin.lz");
u16 Tsa7_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa7_EfxLvupBG.bin.lz");
u16 Tsa8_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa8_EfxLvupBG.bin.lz");
u16 Tsa9_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa9_EfxLvupBG.bin.lz");
u16 Tsa10_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa10_EfxLvupBG.bin.lz");
u16 Tsa11_EfxLvupBG[] = INCBIN_U16("graphics/unsorted/Tsa11_EfxLvupBG.bin.lz");
u16 Img_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Img_EfxLvupBG2.4bpp.lz");
u16 Pal_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Pal_EfxLvupBG2.gbapal");
u16 Pal_EfxLvupBGCOL[] = INCBIN_U16("graphics/unsorted/Pal_EfxLvupBGCOL.gbapal");
u16 Tsa1_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa1_EfxLvupBG2.bin.lz");
u16 Tsa2_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa2_EfxLvupBG2.bin.lz");
u16 Tsa3_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa3_EfxLvupBG2.bin.lz");
u16 Tsa4_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa4_EfxLvupBG2.bin.lz");
u16 Tsa5_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa5_EfxLvupBG2.bin.lz");
u16 Tsa6_EfxLvupBG2[] = INCBIN_U16("graphics/unsorted/Tsa6_EfxLvupBG2.bin.lz");
u16 Img_EfxLvupOBJ2[] = INCBIN_U16("graphics/unsorted/Img_EfxLvupOBJ2.4bpp.lz");
u16 AnimSprite_EfxLvupOBJ2_085C69C8[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C69C8.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6A04[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6A04.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6A58[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6A58.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6AC4[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6AC4.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6B48[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6B48.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6BCC[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6BCC.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6C5C[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6C5C.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6CEC[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6CEC.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6D70[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6D70.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6DF4[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6DF4.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6E84[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6E84.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6F14[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6F14.bin");
u16 AnimSprite_EfxLvupOBJ2_085C6FB0[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6FB0.bin");
u16 AnimSprite_EfxLvupOBJ2_085C704C[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C704C.bin");
u16 AnimSprite_EfxLvupOBJ2_085C70E8[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C70E8.bin");
u16 AnimSprite_EfxLvupOBJ2_085C7178[] = INCBIN_U16("graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C7178.bin");
AnimScr AnimScr_EfxLvupOBJ2[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C69C8, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6A04, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6A58, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6AC4, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6B48, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6BCC, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6C5C, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6CEC, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6D70, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6DF4, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6E84, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6F14, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C6FB0, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C704C, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C70E8, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_EfxLvupOBJ2_085C7178, 10),
    ANIMSCR_BLOCKED
};