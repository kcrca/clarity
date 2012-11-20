// This is part of Connected Textures Mod for Minecraft
// Not recommended for watching to children, pregnant women and people with weak nerves.
// License: GPLv3
// Official thread: http://www.minecraftforum.net/index.php?showtopic=228862
// Author: morpheus
// Author email: morpheus(at)iname(dot)com
package net.minecraft.src;

import org.lwjgl.opengl.GL11;
import java.util.Properties;
import java.io.FileInputStream;
import java.io.IOException;
import java.lang.reflect.*;
import net.minecraft.client.Minecraft;

public class mod_ctm extends BaseMod {

  public static int renderType;
  public static int ctmTexture = -1;
  public static int terrainTexture = -1;
  
  private Properties properties = new Properties();
  public static boolean glassEnabled = true;
  public static boolean sandstoneEnabled = true;
  public static boolean bookshelfEnabled = true;
  public static boolean fastGraphics = false;
  public static boolean isGlassHarvestable = false;
  public static boolean isBookshelfHarvestable = false;
  public static boolean debug = false;
  
  public void load() {
    try {
      String path = Minecraft.getMinecraftDir().getCanonicalPath() + "/mods/ctm.properties";
      FileInputStream file = new FileInputStream(path);
      properties.load(file);
      file.close();
      glassEnabled = Boolean.parseBoolean(properties.getProperty("glassEnabled"));
      sandstoneEnabled = Boolean.parseBoolean(properties.getProperty("sandstoneEnabled"));
      bookshelfEnabled = Boolean.parseBoolean(properties.getProperty("bookshelfEnabled"));
      fastGraphics = Boolean.parseBoolean(properties.getProperty("fastGraphics"));
      isGlassHarvestable = Boolean.parseBoolean(properties.getProperty("isGlassHarvestable"));
      isBookshelfHarvestable = Boolean.parseBoolean(properties.getProperty("isBookshelfHarvestable"));
      ModLoader.getLogger().info("[CTM] Properties file read succesfully!");
    } catch (IOException e) {
      ModLoader.getLogger().warning("[CTM] Unable to read from properties, using default settings.");
    }
    renderType = ModLoader.getUniqueBlockModelID(this, true);
    
    Block newBlocksList[] = Block.blocksList;
    if (glassEnabled)
      newBlocksList[20] = null;
    if (sandstoneEnabled)
      newBlocksList[24] = null;
    if (bookshelfEnabled)
      newBlocksList[47] = null;
    try {
      setFinalStatic(Block.class.getField("m"), newBlocksList);
      if (glassEnabled)
        setFinalStatic(Block.class.getField("M"), (new ctm_BlockGlass(20, 49, Material.glass, false)).setHardness(0.3F).setStepSound(Block.soundGlassFootstep).setBlockName("glass"));
      if (sandstoneEnabled)
        setFinalStatic(Block.class.getField("Q"), (new ctm_BlockSandStone(24)).setStepSound(Block.soundStoneFootstep).setHardness(0.8F).setBlockName("sandStone"));
      if (bookshelfEnabled)
        setFinalStatic(Block.class.getField("an"), (new ctm_BlockBookshelf(47, 35)).setHardness(1.5F).setStepSound(Block.soundWoodFootstep).setBlockName("bookshelf"));
    } catch (Exception e) {
      System.out.println("[CTM] Reflection exception: " + e.getMessage());
    }
  }

  private void setFinalStatic(Field field, Object newValue) throws Exception {
    field.setAccessible(true);
    Field modifiersField = Field.class.getDeclaredField("modifiers");
    modifiersField.setAccessible(true);
    modifiersField.setInt(field, field.getModifiers() & ~Modifier.FINAL);
    field.set(null, newValue);
  }
 
  public String getVersion() {
    return "1.4.1 1.2.5";
  }

  public void renderInvBlock(RenderBlocks renderblocks, Block block, int i, int j) {
    if (j != renderType)
      return;
    RenderEngine rE = ModLoader.getMinecraftInstance().renderEngine;
    if (ctmTexture == -1)
      ctmTexture = rE.getTexture("/ctm.png");
    if (terrainTexture == -1)
      terrainTexture = rE.getTexture("/terrain.png");
    rE.bindTexture(ctmTexture);
    block.setBlockBoundsForItemRender();
    GL11.glTranslatef(-0.5F, -0.5F, -0.5F);
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(0.0F, -1F, 0.0F);
    renderblocks.renderBottomFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(0, i));
    Tessellator.instance.draw();
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(0.0F, 1.0F, 0.0F);
    renderblocks.renderTopFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(1, i));
    Tessellator.instance.draw();
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(0.0F, 0.0F, -1F);
    renderblocks.renderEastFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(2, i));
    Tessellator.instance.draw();
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(0.0F, 0.0F, 1.0F);
    renderblocks.renderWestFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(3, i));
    Tessellator.instance.draw();
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(-1F, 0.0F, 0.0F);
    renderblocks.renderNorthFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(4, i));
    Tessellator.instance.draw();
    Tessellator.instance.startDrawingQuads();
    Tessellator.instance.setNormal(1.0F, 0.0F, 0.0F);
    renderblocks.renderSouthFace(block, 0.0D, 0.0D, 0.0D, block.getBlockTextureFromSideAndMetadata(5, i));
    Tessellator.instance.draw();
    GL11.glTranslatef(0.5F, 0.5F, 0.5F);
    rE.bindTexture(terrainTexture);
  }

  public boolean renderWorldBlock(RenderBlocks renderblocks, IBlockAccess iblockaccess, int i, int j, int k, Block block, int l) {
    if (l != renderType)
      return false;
	  
    RenderEngine rE = ModLoader.getMinecraftInstance().renderEngine;
    if (ctmTexture == -1)
      ctmTexture = rE.getTexture("/ctm.png");
    if (terrainTexture == -1)
      terrainTexture = rE.getTexture("/terrain.png");
      
    if (renderblocks.overrideBlockTexture == -1) {
      Tessellator.instance.draw();
      Tessellator.instance.startDrawingQuads();
     rE.bindTexture(ctmTexture);
    }
    
    renderblocks.cfgGrassFix = false;
    boolean buf = renderblocks.renderStandardBlock(block, i, j, k);
    renderblocks.cfgGrassFix = true;
    
    if (renderblocks.overrideBlockTexture == -1) {
      Tessellator.instance.draw();
      Tessellator.instance.startDrawingQuads();
      rE.bindTexture(terrainTexture);
    }
    return buf;
  }

}