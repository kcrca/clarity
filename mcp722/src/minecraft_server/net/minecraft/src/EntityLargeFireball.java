package net.minecraft.src;

public class EntityLargeFireball extends EntityFireball
{
    public EntityLargeFireball(World par1World)
    {
        super(par1World);
    }

    public EntityLargeFireball(World par1World, EntityLiving par2EntityLiving, double par3, double par5, double par7)
    {
        super(par1World, par2EntityLiving, par3, par5, par7);
    }

    /**
     * Called when this EntityFireball hits a block or entity.
     */
    protected void onImpact(MovingObjectPosition par1MovingObjectPosition)
    {
        if (!this.worldObj.isRemote)
        {
            if (par1MovingObjectPosition.entityHit != null)
            {
                par1MovingObjectPosition.entityHit.attackEntityFrom(DamageSource.causeFireballDamage(this, this.shootingEntity), 6);
            }

            this.worldObj.newExplosion((Entity)null, this.posX, this.posY, this.posZ, 1.0F, true, this.worldObj.getGameRules().getGameRuleBooleanValue("mobGriefing"));
            this.setDead();
        }
    }
}
