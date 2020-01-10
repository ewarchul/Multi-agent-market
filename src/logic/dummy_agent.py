from spade import agent

class DummyAgent(agent.Agent):
   async def setup(self):
        print("xD to ja {}".format(str(self.jid)))



dummy = DummyAgent("hehe", "hehe")

dummy.start()


dummy.stop()



