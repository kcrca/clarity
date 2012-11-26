package net.minecraft.src;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;

public class mod_ken extends BaseMod {
    static int renderType;

    private static final int GLASS_BLOCK_INDEX = 20;

    @Override
    public String getVersion() {
        return "1.4.1 1.2.5";
    }

    public void load() {
        renderType = ModLoader.getUniqueBlockModelID(this, true);

        try {
            BlockGlass origGlass =
                    (BlockGlass) Block.blocksList[GLASS_BLOCK_INDEX];
            assert GLASS_BLOCK_INDEX == origGlass.blockID;
            Block.blocksList[GLASS_BLOCK_INDEX] = null;
            ken_BlockGlass newGlass = new ken_BlockGlass(origGlass);
            setFinalStatic(Block.class, "M", "glass", newGlass);
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("[CTM] Reflection exception: " + e.getMessage());
        }
    }

    private void setFinalStatic(Class cls, String mangledName, String clearName,
            Object newValue) throws Exception {

        Field field;
        try {
            field = cls.getField(mangledName);
        } catch (NoSuchFieldException e) {
            field = cls.getField(clearName);
        }
        field.setAccessible(true);
        Field modifiersField = Field.class.getDeclaredField("modifiers");
        modifiersField.setAccessible(true);
        modifiersField.setInt(field, field.getModifiers() & ~Modifier.FINAL);
        field.set(null, newValue);
    }
    
    public static String blockName(Block block) {
        String origName = block.getBlockName();
        if (origName.startsWith("tile."))
            origName = origName.substring(5);
        return origName;
    }
}