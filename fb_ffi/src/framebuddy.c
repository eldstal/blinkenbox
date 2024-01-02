// Include the header file to get access to the MicroPython API
#include "py/dynruntime.h"


// This is the function which will be called from Python, as set(fb_addr, n_frames, word_index, bit_index, pwm_bits)
// There's no macro for a fixed four-argument function, so we're doing vararg. Yuck.
STATIC void* setbits(size_t n_args, const mp_obj_t* args) {
    // Extract the integer from the MicroPython input object

    if (n_args != 5) return (void*) 0xdeadbeef;

    uint32_t* fb = (uint32_t*) mp_obj_get_int(args[0]);
    mp_int_t n_frames  = mp_obj_get_int(args[1]);
    mp_int_t w  = mp_obj_get_int(args[2]);
    mp_int_t b  = mp_obj_get_int(args[3]);
    mp_int_t pwm_bits = mp_obj_get_int(args[4]);


    for (uint32_t f=0; f<n_frames; f++) {
        uint32_t* word = &(fb[f*8 + w]);

        if ((pwm_bits >> f) & 1) {
            *word = *word | (1 << b);
        } else {
            *word = *word & ~(1 << b);
        }
    }


    // Convert the result to a MicroPython integer object and return it
    return (void*) 0;
}
// Define a Python reference to the function above
//STATIC MP_DEFINE_CONST_FUN_OBJ_4(set_obj, setbits);
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(setbits_obj, 5, 5, setbits);

// This is the function which will be called from Python, as set(fb_addr, n_frames, word_index, bit_index, pwm_bits)
// There's no macro for a fixed four-argument function, so we're doing vararg. Yuck.
STATIC void* transform_setbits(size_t n_args, const mp_obj_t* args) {
    // Extract the integer from the MicroPython input object

    if (n_args != 5) return (void*) 0xdeadbeef;

    uint32_t* fb = (uint32_t*) mp_obj_get_int(args[0]);
    mp_int_t n_frames  = mp_obj_get_int(args[1]);
    mp_int_t x  = mp_obj_get_int(args[2]);
    mp_int_t y  = mp_obj_get_int(args[3]);
    mp_int_t pwm_bits = mp_obj_get_int(args[4]);


    x = x & 0xF;
    y = y & 0xF;

    // Index into our framebuffer (word-width)
    size_t w = 0;

    // Right half of frame
    if (x >=8) w += 4;

    // Vertical position
    w += y/4;

    size_t b = (y%4)*8 + x%8;

    for (uint32_t f=0; f<n_frames; f++) {
        uint32_t* word = &(fb[f*8 + w]);

        if ((pwm_bits >> f) & 1) {
            *word = *word | (1 << b);
        } else {
            *word = *word & ~(1 << b);
        }
    }


    // Convert the result to a MicroPython integer object and return it
    return (void*) 0;
}
// Define a Python reference to the function above
//STATIC MP_DEFINE_CONST_FUN_OBJ_4(set_obj, setbits);
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(transform_setbits_obj, 5, 5, transform_setbits);

// This is the entry point and is called when the module is imported
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    // This must be first, it sets up the globals dict and other things
    MP_DYNRUNTIME_INIT_ENTRY

    // Make the functions available in the module's namespace
    mp_store_global(MP_QSTR_setbits, MP_OBJ_FROM_PTR(&setbits_obj));
    mp_store_global(MP_QSTR_transform_setbits, MP_OBJ_FROM_PTR(&transform_setbits_obj));

    // This must be last, it restores the globals dict
    MP_DYNRUNTIME_INIT_EXIT
}