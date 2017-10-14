import unittest
from arky.api import Block, Account, Delegate, Loader, Multisignature, Peer, Signature, Transport


class TestBlockAPI(unittest.TestCase):
    def test_getBlocks(self, **params):
        req = Block.getBlocks(**params)
        self.assertEqual(req['success'], True)

    def test_getBlock(self, **params):
        req = Block.getBlock(id="1428222761775706806", **params)
        self.assertEqual(req['success'], False)

    def test_getNetHash(self, **params):
        req = Block.getNethash(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainFee(self, **params):
        req = Block.getBlockchainFee(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainFees(self, **params):
        req = Block.getBlockchainFees(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainHeight(self, **params):
        req = Block.getBlockchainHeight(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainEpoch(self, **params):
        req = Block.getBlockchainEpoch(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainMilestone(self, **params):
        req = Block.getBlockchainMilestone(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainReward(self, **params):
        req = Block.getBlockchainReward(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainSupply(self, **params):
        req = Block.getBlockchainSupply(**params)
        self.assertEqual(req['success'], True)

    def test_getBlockchainStatus(self, **params):
        req = Block.getBlockchainStatus(**params)
        self.assertEqual(req['success'], True)

    #def test_getForgedByAccount(self, publicKey, **params):
    #    print(Block.getForgedByAccount("038e82be3e92018374c9b53a25a428799602366635d5270c5154d945ac60216ffe", **params))


class TestAccountAPI(unittest.TestCase):
    def test_getDelegateFee(self, **params):
        req = Account.getDelegateFee(**params)
        self.assertEqual(req['success'], True)

    def test_getTopAcounts(self, **params):
        """
        Unable to make this function works because of a API bad enpoint error
        """
        req = Account.getTopAccounts()
        print(req)
        self.assertEqual(req['success'], True)


class TestDelegateAPI(unittest.TestCase):
    def test_getDelegates(self):
        r = Delegate.getDelegates()
        self.assertEqual(r['success'], True)

    def test_getDelegate(self):
        """
        Same, should work, but the get function doesn't build correctly the URL I guess
        """
        r = Delegate.getDelegate(username="dr10")
        self.assertEqual(r['success'], True)


class TestLoaderAPI(unittest.TestCase):
    def test_getLoadingStatus(self):
        r = Loader.getLoadingStatus()
        self.assertEqual(r['success'], True)

    def test_getSynchronisationStatus(self):
        r = Loader.getSynchronisationStatus()
        self.assertEqual(r['success'], True)

    def test_getAutoConfigure(self):
        r = Loader.getAutoConfigure()
        self.assertEqual(r['success'], True)


class TestMultisignature(unittest.TestCase):
    def test_getPendingMultiSignatureTransactions(self):
        r = Multisignature.getPendingMultiSignatureTransactions("021d03bace0687a1a5e797f884b13fb46f817ec32de1374a7f223f24404401d220")
        self.assertEqual(r['success'], True)

    def test_getAccountsOfMultisignature(self):
        r = Multisignature.getAccountsOfMultisignature("021d03bace0687a1a5e797f884b13fb46f817ec32de1374a7f223f24404401d220")
        self.assertEqual(r['success'], True)


class TestPeer(unittest.TestCase):
    def test_getPeersList(self):
        r = Peer.getPeersList()
        self.assertEqual(r['success'], True)

    def test_getPeer(self):
        r = Peer.getPeer("127.0.0.1", "4001")
        self.assertEqual(r['success'], True)

    def test_getPeerVersion(self):
        r = Peer.getPeerVersion()
        self.assertEqual(r['success'], True)


class TestSignature(unittest.TestCase):
    def test_getSignatureFee(self):
        r = Signature.getSignatureFee("ATdnKCcvtfZWjgPj4Az4prKPVRNA7fKBQr")
        self.assertEqual(r["success"], True)


class TransportTest(unittest.TestCase):
    def test_getPeersList(self):
        r = Transport.getPeersList()
        self.assertEqual(r["success"], True)

    def test_getBlocksByIds(self):
        r = Transport.getBlocksByIds("15620682673815497133")
        self.assertEqual(r["success"], True)

    def test_getBlock(self):
        r = Transport.getBlock("AUexKjGtgsSpVzPLs6jNMM6vJ6znEVTQWK")
        self.assertEqual(r["success"], True)

    def test_getBlocks(self):
        r = Transport.getBlocks("AUexKjGtgsSpVzPLs6jNMM6vJ6znEVTQWK")
        self.assertEqual(r["success"], True)

    def test_getTransactions(self):
        r = Transport.getTransactions()
        self.assertEqual(r["success"], True)

    def test_getTransactionsFromIds(self):
        r = Transport.getTransactionsFromIds("15620682673815497133")
        self.assertEqual(r["success"], True)

    def test_getHeight(self):
        r = Transport.getHeight()
        self.assertEqual(r["success"], True)

    def test_getStatus(self):
        r = Transport.getStatus()
        self.assertEqual(r["success"], True)

if __name__ == '__main__':
    unittest.main()