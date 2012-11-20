package net.minecraft.src;

public final class ThreadDedicatedServer extends Thread
{
    final DedicatedServer field_82012_a;

    public ThreadDedicatedServer(DedicatedServer par1DedicatedServer)
    {
        this.field_82012_a = par1DedicatedServer;
    }

    public void run()
    {
        this.field_82012_a.stopServer();
    }
}
