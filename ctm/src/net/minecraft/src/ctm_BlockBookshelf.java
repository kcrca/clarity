// This is part of Connected Textures Mod for Minecraft
// Not recommended for watching to children, pregnant women and people with weak nerves.
// License: GPLv3
// Official thread: http://www.minecraftforum.net/index.php?showtopic=228862
// Author: morpheus
// Author email: morpheus(at)iname(dot)com
package net.minecraft.src;

import java.util.Random;

public class ctm_BlockBookshelf extends BlockBookshelf {

  public ctm_BlockBookshelf(int i, int j) {
    super(i, j);
  }

  public int getRenderType() {
    return mod_ctm.renderType;
  }

  public int quantityDropped(Random random)
  {
      return (mod_ctm.isBookshelfHarvestable ? 1 : 0);
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
    if(i <= 1) return 28;
    return 15;
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
    int texture = 0;
    boolean b[] = new boolean[4];
    b[0] = isShouldBeConnected(iblockaccess, x - 1, y, z, i);
    b[1] = isShouldBeConnected(iblockaccess, x + 1, y, z, i);
    b[2] = isShouldBeConnected(iblockaccess, x, y, z + 1, i);
    b[3] = isShouldBeConnected(iblockaccess, x, y, z - 1, i);
    if(i <= 1)
      texture = 28;
    else if (i == 2) {
      if (!b[0] && !b[1]) texture = 15;
      else if (b[0] && !b[1]) texture = 12;
      else if (!b[0] && b[1]) texture = 14;
      else if (b[0] && b[1]) texture = 13;
    } else if (i == 3) {
      if (!b[0] && !b[1]) texture = 15;
      else if (b[0] && !b[1]) texture = 14;
      else if (!b[0] && b[1]) texture = 12;
      else if (b[0] && b[1]) texture = 13;
    } else if (i == 4) {
      if (!b[2] && !b[3]) texture = 15;
      else if (b[2] && !b[3]) texture = 12;
      else if (!b[2] && b[3]) texture = 14;
      else if (b[2] && b[3]) texture = 13;
    } else if (i == 5) {
      if (!b[2] && !b[3]) texture = 15;
      else if (b[2] && !b[3]) texture = 14;
      else if (!b[2] && b[3]) texture = 12;
      else if (b[2] && b[3]) texture = 13;
    }
    return texture;
  }
  
  private boolean isShouldBeConnected(IBlockAccess iblockaccess, int x, int y, int z, int i) {
    int x2 = x;
    int y2 = y;
    int z2 = z;
    if (i == 0) y2--;
    else if (i == 1) y2++;
    else if (i == 2) z2--;
    else if (i == 3) z2++;
    else if (i == 4) x2--;
    else if (i == 5) x2++;
    return ((iblockaccess.getBlockId(x, y, z) == blockID) && !iblockaccess.isBlockOpaqueCube(x2, y2, z2));
  }
  
}
