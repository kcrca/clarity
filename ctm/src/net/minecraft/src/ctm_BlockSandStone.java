// This is part of Connected Textures Mod for Minecraft
// Not recommended for watching to children, pregnant women and people with weak nerves.
// License: GPLv3
// Official thread: http://www.minecraftforum.net/index.php?showtopic=228862
// Author: morpheus
// Author email: morpheus(at)iname(dot)com
package net.minecraft.src;

public class ctm_BlockSandStone extends BlockSandStone {

  public ctm_BlockSandStone(int i) {
    super(i);
  }

  public int getRenderType() {
    return mod_ctm.renderType;
  }
  
  public int getBlockTextureFromSide(int i) {
    // If called not from CTM - call parent's method
    boolean isFromCtm = false;
    for (StackTraceElement e : (new Throwable()).getStackTrace())
      if (e.getClassName() == "mod_ctm") {
        isFromCtm = true;
        break;
      }
    if (!isFromCtm)
      return super.getBlockTextureFromSide(i);
    // New code:
    if(i == 1)
      return 64;
    if(i == 0)
      return 67;
    return 65;
  }
    
  public int getBlockTexture(IBlockAccess iblockaccess, int x, int y, int z, int i) {
    // If called not from CTM - call parent's method
    boolean isFromCtm = false;
    for (StackTraceElement e : (new Throwable()).getStackTrace())
      if (e.getClassName() == "mod_ctm") {
        isFromCtm = true;
        break;
      }
    if (!isFromCtm)
      return super.getBlockTexture(iblockaccess,x,y,z,i);
    // New code:
    if(i == 1)
      return 64;
    else if(i == 0)
      return 67;
    else if (!isShouldBeConnected(iblockaccess, x, y + 1, z, i))
      return 65;
    return 66;
  }
  
  private boolean isShouldBeConnected(IBlockAccess iblockaccess, int x, int y, int z, int i) {
    int x2 = x;
    int y2 = y;
    int z2 = z;
    if (i == 2) z2--;
    else if (i == 3) z2++;
    else if (i == 4) x2--;
    else if (i == 5) x2++;
    return ((iblockaccess.getBlockId(x, y, z) == blockID) && !iblockaccess.isBlockOpaqueCube(x2, y2, z2));
  }
  
}
