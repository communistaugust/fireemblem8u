    .include "animscr.inc"
	.section .data

	.global Img_LvupApfx
Img_LvupApfx:  @ 0x085BB0C8
	.incbin "./graphics/lvup/LvupAp.4bpp.lz"

	.global Pal_LvupApfx
Pal_LvupApfx:  @ 0x085BB2DC
	.incbin "./graphics/lvup/LvupAp.gbapal", 0x0, 0x20

    .incbin "graphics/unsorted/gUnknown_085bb2fc.bin"

	.global Img_ArenaBattleBg
Img_ArenaBattleBg:  @ 0x085BC188
	.incbin "graphics/unsorted/Img_ArenaBattleBg.4bpp.lz"

	.global Tsa_ArenaBattleBg
Tsa_ArenaBattleBg:  @ 0x085BE7F4
	.incbin "graphics/unsorted/Tsa_ArenaBattleBg.bin.lz"

	.global Pal_ArenaBattleBg_A
Pal_ArenaBattleBg_A:  @ 0x085BEF94
	.incbin "graphics/unsorted/Pal_ArenaBattleBg_A.gbapal"

	.global Pal_ArenaBattleBg_B
Pal_ArenaBattleBg_B:  @ 0x085BF014
	.incbin "graphics/unsorted/Pal_ArenaBattleBg_B.gbapal"

	.global Pal_ArenaBattleBg_C
Pal_ArenaBattleBg_C:  @ 0x085BF094
	.incbin "graphics/unsorted/Pal_ArenaBattleBg_C.gbapal"

	.incbin "graphics/unsorted/gUnknown_085bf114.bin"

	.global Img1_EfxLvupBG
Img1_EfxLvupBG:
	.incbin "graphics/unsorted/Img1_EfxLvupBG.bin.lz"

	.global Img2_EfxLvupBG
Img2_EfxLvupBG:
	.incbin "graphics/unsorted/Img2_EfxLvupBG.bin.lz"

	.global Img3_EfxLvupBG
Img3_EfxLvupBG:
	.incbin "graphics/unsorted/Img3_EfxLvupBG.bin.lz"

	.global Img4_EfxLvupBG
Img4_EfxLvupBG:
	.incbin "graphics/unsorted/Img4_EfxLvupBG.bin.lz"

	.global Img5_EfxLvupBG
Img5_EfxLvupBG:
	.incbin "graphics/unsorted/Img5_EfxLvupBG.bin.lz"

	.global Img6_EfxLvupBG
Img6_EfxLvupBG:
	.incbin "graphics/unsorted/Img6_EfxLvupBG.bin.lz"

	.global Img7_EfxLvupBG
Img7_EfxLvupBG:
	.incbin "graphics/unsorted/Img7_EfxLvupBG.bin.lz"

	.global Pal_EfxLvupBG
Pal_EfxLvupBG:  @ 0x085C48AC
	.incbin "graphics/unsorted/Pal_EfxLvupBG.gbapal"

    .global Tsa1_EfxLvupBG
Tsa1_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa1_EfxLvupBG.bin.lz"

    .global Tsa2_EfxLvupBG
Tsa2_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa2_EfxLvupBG.bin.lz"

    .global Tsa3_EfxLvupBG
Tsa3_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa3_EfxLvupBG.bin.lz"

    .global Tsa4_EfxLvupBG
Tsa4_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa4_EfxLvupBG.bin.lz"

    .global Tsa5_EfxLvupBG
Tsa5_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa5_EfxLvupBG.bin.lz"

    .global Tsa6_EfxLvupBG
Tsa6_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa6_EfxLvupBG.bin.lz"

    .global Tsa7_EfxLvupBG
Tsa7_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa7_EfxLvupBG.bin.lz"

    .global Tsa8_EfxLvupBG
Tsa8_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa8_EfxLvupBG.bin.lz"

    .global Tsa9_EfxLvupBG
Tsa9_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa9_EfxLvupBG.bin.lz"

    .global Tsa10_EfxLvupBG
Tsa10_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa10_EfxLvupBG.bin.lz"

    .global Tsa11_EfxLvupBG
Tsa11_EfxLvupBG:
    .incbin "graphics/unsorted/Tsa11_EfxLvupBG.bin.lz"

	.global Img_EfxLvupBG2
Img_EfxLvupBG2:  @ 0x085C5994
	.incbin "graphics/unsorted/Img_EfxLvupBG2.4bpp.lz"

	.global Pal_EfxLvupBG2
Pal_EfxLvupBG2:  @ 0x085C6054
	.incbin "graphics/unsorted/Pal_EfxLvupBG2.gbapal"

	.global Pal_EfxLvupBGCOL
Pal_EfxLvupBGCOL:  @ 0x085C60D4
	.incbin "graphics/unsorted/Pal_EfxLvupBGCOL.gbapal"

    .global Tsa1_EfxLvupBG2
Tsa1_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa1_EfxLvupBG2.bin.lz"

    .global Tsa2_EfxLvupBG2
Tsa2_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa2_EfxLvupBG2.bin.lz"

    .global Tsa3_EfxLvupBG2
Tsa3_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa3_EfxLvupBG2.bin.lz"

    .global Tsa4_EfxLvupBG2
Tsa4_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa4_EfxLvupBG2.bin.lz"

    .global Tsa5_EfxLvupBG2
Tsa5_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa5_EfxLvupBG2.bin.lz"

    .global Tsa6_EfxLvupBG2
Tsa6_EfxLvupBG2:
    .incbin "graphics/unsorted/Tsa6_EfxLvupBG2.bin.lz"

	.global Img_EfxLvupOBJ2
Img_EfxLvupOBJ2:  @ 0x085C6730
	.incbin "graphics/unsorted/Img_EfxLvupOBJ2.4bpp.lz"

	.global AnimSprite_EfxLvupOBJ2_085C69C8
AnimSprite_EfxLvupOBJ2_085C69C8:	@ 0x085C69C8
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C69C8.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6A04
AnimSprite_EfxLvupOBJ2_085C6A04:	@ 0x085C6A04
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6A04.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6A58
AnimSprite_EfxLvupOBJ2_085C6A58:	@ 0x085C6A58
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6A58.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6AC4
AnimSprite_EfxLvupOBJ2_085C6AC4:	@ 0x085C6AC4
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6AC4.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6B48
AnimSprite_EfxLvupOBJ2_085C6B48:	@ 0x085C6B48
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6B48.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6BCC
AnimSprite_EfxLvupOBJ2_085C6BCC:	@ 0x085C6BCC
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6BCC.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6C5C
AnimSprite_EfxLvupOBJ2_085C6C5C:	@ 0x085C6C5C
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6C5C.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6CEC
AnimSprite_EfxLvupOBJ2_085C6CEC:	@ 0x085C6CEC
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6CEC.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6D70
AnimSprite_EfxLvupOBJ2_085C6D70:	@ 0x085C6D70
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6D70.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6DF4
AnimSprite_EfxLvupOBJ2_085C6DF4:	@ 0x085C6DF4
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6DF4.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6E84
AnimSprite_EfxLvupOBJ2_085C6E84:	@ 0x085C6E84
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6E84.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6F14
AnimSprite_EfxLvupOBJ2_085C6F14:	@ 0x085C6F14
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6F14.bin"

	.global AnimSprite_EfxLvupOBJ2_085C6FB0
AnimSprite_EfxLvupOBJ2_085C6FB0:	@ 0x085C6FB0
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C6FB0.bin"

	.global AnimSprite_EfxLvupOBJ2_085C704C
AnimSprite_EfxLvupOBJ2_085C704C:	@ 0x085C704C
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C704C.bin"

	.global AnimSprite_EfxLvupOBJ2_085C70E8
AnimSprite_EfxLvupOBJ2_085C70E8:	@ 0x085C70E8
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C70E8.bin"

	.global AnimSprite_EfxLvupOBJ2_085C7178
AnimSprite_EfxLvupOBJ2_085C7178:	@ 0x085C7178
	.incbin "graphics/unsorted/AnimSprite_EfxLvupOBJ2_085C7178.bin"

	.global AnimScr_EfxLvupOBJ2
AnimScr_EfxLvupOBJ2:  @ 0x085C71E4
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C69C8, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6A04, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6A58, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6AC4, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6B48, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6BCC, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6C5C, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6CEC, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6D70, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6DF4, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6E84, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6F14, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C6FB0, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C704C, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C70E8, 1
    ANIMSCR_FORCE_SPRITE AnimSprite_EfxLvupOBJ2_085C7178, 10
    ANIMSCR_BLOCKED
