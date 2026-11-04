#include "global.h"
#include "anime.h"
#include "gba_sprites.h"

u8 Img_EkrLvupNumBig[] = INCBIN_U8("graphics/unsorted/Img_EkrLvupNumBig.4bpp");

struct AnimSpriteData AnimSprite_LvupStatup_1[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -7, -10),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -6, -6),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -4, -4),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_2[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -7, -8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -5, -5),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 2, -19),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -4, -17),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -7, -13),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_3[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -5, -15),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -7, -6),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 11, -12),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 6, -18),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -1, -18),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -7, -11),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_4[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 0, -19),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -7, -10),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 13, -5),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 11, -12),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 7, -17),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -5, -15),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_5[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 9, -14),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -4, -17),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 8, 6),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 13, -1),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 13, -7),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 2, -18),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_6[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 13, -7),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, 4, -18),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -2, 12),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, 8, 8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 13, 2),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 9, -14),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_7[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 13, 2),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, 8, -16),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -16, 10),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -6, 13),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 5, 10),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 13, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_8[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 0, 14),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, 13, -3),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -24, -2),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -20, 8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -12, 15),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, 10, 7),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_9[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -17, 14),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, 8, 8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -25, -17),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -28, -6),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -25, 5),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -4, 16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_10[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -7, 17),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -28, -11),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -22, -22),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -18, 13),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0000, -13, -29),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -27, 2),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_11[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -19, 12),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -25, -18),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -7, -31),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0001, -17, -27),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -25, 4),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0002, -28, -7),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_12[] = {
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0040, -8, -9),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0003, -37, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_13[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -17),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0004, -46, -8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x0006, -30, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_14[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0024, -8, -17),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x0007, -52, -8),
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_8, 0x000B, -20, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_15[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0024, -8, -20),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_16[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -27),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_17[] = {
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0040, -8, -22),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_18[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -25),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_19[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0026, -8, -17),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_20[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0028, -8, -17),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_21[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x002A, -8, -17),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_16, 0x000C, -56, -8),
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0010, -24, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_22[] = {
    ANIM_SPRITE(ATTR0_WIDE, 0x2000, 0x0040, -8, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_23[] = {
    ANIM_SPRITE(ATTR0_SQUARE, 0x6000, 0x0028, -8, -22),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_24[] = {
    ANIM_SPRITE(ATTR0_SQUARE, 0x6000, 0x002A, -8, -22),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_25[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x002C, -8, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_26[] = {
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0040, -8, -9),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_27[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -17),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_28[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0024, -8, -17),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_29[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0024, -8, -20),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_30[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -27),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_31[] = {
    ANIM_SPRITE(ATTR0_WIDE, ATTR1_SIZE_8, 0x0040, -8, -22),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_32[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0022, -8, -25),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_33[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0026, -8, -17),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_34[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x0028, -8, -17),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_35[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x002A, -8, -17),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_36[] = {
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_37[] = {
    ANIM_SPRITE_AFFIN(1, 0x80, 0x0, 0x0, 0x80),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON + OBJ_DISABLE, ATTR1_SIZE_16, 0x002C, -16, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_38[] = {
    ANIM_SPRITE_AFFIN(1, 0x8e, 0x0, 0x0, 0x8e),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON + OBJ_DISABLE, ATTR1_SIZE_16, 0x002C, -16, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_39[] = {
    ANIM_SPRITE_AFFIN(1, 0xa0, 0x0, 0x0, 0xa0),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON + OBJ_DISABLE, ATTR1_SIZE_16, 0x002C, -16, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_40[] = {
    ANIM_SPRITE_AFFIN(1, 0xb7, 0x0, 0x0, 0xb7),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON + OBJ_DISABLE, ATTR1_SIZE_16, 0x002C, -16, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_41[] = {
    ANIM_SPRITE_AFFIN(1, 0xd5, 0x0, 0x0, 0xd5),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON + OBJ_DISABLE, ATTR1_SIZE_16, 0x002C, -16, -16),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_42[] = {
    ANIM_SPRITE(ATTR0_SQUARE, ATTR1_SIZE_16, 0x002C, -8, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_43[] = {
    ANIM_SPRITE_AFFIN(1, 0x141, 0x0, 0x0, 0x141),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON, ATTR1_SIZE_16, 0x002C, -8, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_44[] = {
    ANIM_SPRITE_AFFIN(1, 0x1ac, 0x0, 0x0, 0x1ac),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON, ATTR1_SIZE_16, 0x002C, -8, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_45[] = {
    ANIM_SPRITE_AFFIN(1, 0x282, 0x0, 0x0, 0x282),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON, ATTR1_SIZE_16, 0x002C, -8, -8),
    ANIM_SPRITE_END
    };

struct AnimSpriteData AnimSprite_LvupStatup_46[] = {
    ANIM_SPRITE_AFFIN(1, 0x505, 0x0, 0x0, 0x505),
    ANIM_SPRITE(ATTR0_SQUARE + OBJ_ROT_SCALE_ON, ATTR1_SIZE_16, 0x002C, -8, -8),
    ANIM_SPRITE_END
    };

AnimScr AnimScr_LvupStatupfx1[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_1, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_2, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_3, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_4, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_5, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_6, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_7, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_8, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_9, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_10, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_11, 2),
    ANIMSCR_BLOCKED
    };

AnimScr AnimScr_LvupStatupfx2[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_12, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_13, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_14, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_15, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_16, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_17, 3),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_16, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_18, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_19, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_20, 24),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_21, 8),
    ANIMSCR_BLOCKED,
    };

AnimScr AnimScr_LvupStatupfx3[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_22, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_23, 24),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_24, 8),
    ANIMSCR_BLOCKED
    };

AnimScr AnimScr_LvupStatupfx4[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_36, 15),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_25, 1),
    ANIMSCR_BLOCKED
    };

AnimScr AnimScr_LvupStatupfx5[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_36, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_25, 4),
    ANIMSCR_BLOCKED
    };

AnimScr AnimScr_LvupStatupfx6[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_26, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_27, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_28, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_29, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_30, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_31, 3),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_30, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_32, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_33, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_34, 24),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_35, 8),
    ANIMSCR_BLOCKED
    };

AnimScr AnimScr_LvupStatupObj[] = {
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_37, 4),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_38, 2),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_39, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_40, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_41, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_42, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_43, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_44, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_45, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_46, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_36, 1),
    ANIMSCR_FORCE_SPRITE(AnimSprite_LvupStatup_25, 4),
    ANIMSCR_BLOCKED
    };
