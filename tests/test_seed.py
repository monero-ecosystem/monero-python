#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from monero.address import Address
from monero.seed import Seed
from monero.wordlists import list_wordlists

class SeedTestCase(unittest.TestCase):

    def test_mnemonic_seed(self):
        # Known good 25 word seed phrases should construct a class and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 24 word seed phrases should construct a class, store phrase, and register valid hex
        seed = Seed("wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding")
        self.assertEqual(seed.hex, "8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")

        # Known good 25 word hexadecimal strings should construct a class, store phrase, and register valid hex
        seed = Seed("8ffa9f586b86d294d93731765d192765311bddc76a4fa60311f8af36bbf6fb06")
        self.assertEqual(seed.phrase, "wedge going quick racetrack auburn physics lectures light waist axes whipped habitat square awkward together injury niece nugget guarded hive obnoxious waxing faked folding square")
        self.assertTrue(len(seed.hex) % 8 == 0)

        # Known good 13 word seed phrases should construct a class and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 12 word seed phrases should construct a class, store phrase, and register valid hex
        seed = Seed("ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin")
        self.assertEqual(seed.hex, "932d70711acc2d536ca11fcb79e05516")

        # Known good 13 word hexadecimal strings should construct a class, store phrase, and register valid hex
        seed = Seed("932d70711acc2d536ca11fcb79e05516")
        self.assertEqual(seed.phrase, "ought knowledge upright innocent eldest nerves gopher fowls below exquisite aces basin fowls")
        self.assertTrue(len(seed.hex) % 8 == 0)

        # Generated seed phrases should be 25 words, register valid hex
        seed = Seed()
        seed_split = seed.phrase.split(" ")
        self.assertTrue(len(seed_split) == 25)
        self.assertTrue(len(seed.hex) % 8 == 0)

        # Invalid phrases should not be allowed
        with self.assertRaises(ValueError) as ts:
            Seed("oh damn you thought fool")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed("Thi5isMyS3cr3tPa55w0rd")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed(" ")
        self.assertEqual(ts.expected, ValueError)
        with self.assertRaises(ValueError) as ts:
            Seed("\\x008")
        self.assertEqual(ts.expected, ValueError)


    def test_keys(self):
        seed = Seed("adjust mugged vaults atlas nasty mews damp toenail suddenly toxic possible "\
            "framed succeed fuzzy return demonstrate nucleus album noises peculiar virtual "\
            "rowboat inorganic jester fuzzy")
        self.assertFalse(seed.is_mymonero())
        self.assertEqual(
            seed.secret_spend_key(),
            '482700617ba810f94035d7f4d7ccc1a29878e165b4867872b705204c85406906')
        self.assertEqual(
            seed.secret_view_key(),
            '09ed72c713d3e9e19bef2f5204cf85f6cb25de7842aa0722abeb12697f171903')
        self.assertEqual(
            seed.public_spend_key(),
            '4ee576f52b9c6a824a3d5c2832d117177d2bb9992507c2c78788bb8dbaf4b640')
        self.assertEqual(
            seed.public_view_key(),
            'e1ef99d66312ec0b16b17c66c591ab59594e21621588b63b62fa69fe615a768e')
        self.assertEqual(
            seed.public_address(),
            '44cWztNFdAqNnycvZbUoj44vsbAEmKnx9aNgkjHdjtMsBrSeKiY8J4s2raH7EMawA2Fwo9utaRTV7Aw8EcTMNMxhH4YtKdH')
        self.assertIsInstance(seed.public_address(), Address)
        self.assertEqual(
            seed.public_address(net='stage'),
            '54pZ5jHDGmwNnycvZbUoj44vsbAEmKnx9aNgkjHdjtMsBrSeKiY8J4s2raH7EMawA2Fwo9utaRTV7Aw8EcTMNMxhH6cuARW')
        self.assertIsInstance(seed.public_address(net='stage'), Address)

        seed = Seed("dwelt idols lopped blender haggled rabbits piloted value swagger taunts toolbox upgrade swagger")
        self.assertTrue(seed.is_mymonero())
        # check if the same seed without checksum matches the hex
        self.assertEqual(seed.hex, Seed(" ".join(seed.phrase.split(" ")[:12])).hex)
        # the following fails, #21 addresses that
        self.assertEqual(
            seed.secret_spend_key(),
            'a67505f92004dd6242b64acd16e34ecf788a2d28b6072091e054238d84591403')
        self.assertEqual(
            seed.secret_view_key(),
            '83f652cb370948c8cbcf06839df043aa8c0d0ed36e38b3c827c4c00370af1a0f')
        self.assertEqual(
            seed.public_address(),
            '47dwi1w9it69yZyTBBRD52ctQqw3B2FZx79bCEgVUKGHH2m7MjmaXrjeQfchMMkarG6AF9a36JvBWCyRaqEcUixpKLQRxdj')
        self.assertIsInstance(seed.public_address(), Address)

    def test_languages(self):
        for wordlist in list_wordlists():
            # Generate random seed
            seed = Seed(wordlist=wordlist)

            # Convert it from phrase
            seed_from_phrase = Seed(seed.phrase, wordlist=wordlist)
            self.assertEqual(seed.hex, seed_from_phrase.hex)
            self.assertEqual(seed.phrase, seed_from_phrase.phrase)

            # Convert it from hex
            seed_from_hex = Seed(seed.hex, wordlist=wordlist)
            self.assertEqual(seed.hex, seed_from_hex.hex)
            self.assertEqual(seed.phrase, seed_from_hex.phrase)

    def test_chinese_simplified(self):
        seed = Seed(u"遭 牲 本 点 司 司 仲 吉 虎 只 绝 生 指 纯 伟 破 夫 惊 群 楚 祥 旋 暗 骨 伟", "Chinese (simplified)")
        self.assertEqual(
            seed.secret_spend_key(),
            '2ec46011b23b0c00468946f1d9a64995bf0a89f9ee0bbf4f64058a3acd81a70e')
        self.assertEqual(
            seed.secret_view_key(),
            'aa141796baa24539583306300b44a72495bb7823a0cc6ad856de6d372288d10f')
        self.assertEqual(
            seed.public_spend_key(),
            '76cc3b927e70fee85a43a6141d019b53c77f46bbcd6c4dc6d814dfc271af361c')
        self.assertEqual(
            seed.public_view_key(),
            '91ef3783492e173ca366a818ae7ee37f062daea909fd9ed9ca40d41e7d572dd4')
        self.assertEqual(
            seed.public_address(),
            '468Dewci4TPfs7TATZ2nf4F1mKAEMp6RraG37wiSU4uT5nAbBwGz5LaB9GWHG23o6ANFJ1Q9cBYk5dRqWNNkmFN4Qx3RqBD')

    def test_dutch(self):
        seed = Seed(u"ralf tolvrij copier roon ossuarium wedstrijd splijt debbie bomtapijt occlusie oester noren hiaat scenario geshockt veeteler rotten symboliek jarig bock yoghurt plegen weert zeeblauw wedstrijd", "Dutch")
        self.assertEqual(
            seed.secret_spend_key(),
            '600d3c5022e1844dd2df02f178a074fc2e566793e99d9e1465926adcbfa9b508')
        self.assertEqual(
            seed.secret_view_key(),
            'bb8984647124dafcb8682f1c257b5232bb12b96d682bfc320b4f8ce935e2d303')
        self.assertEqual(
            seed.public_spend_key(),
            'df4be25f7ccaf632f1525b06fd9b0d7e9f64b21ebfb609353d643a24de16221b')
        self.assertEqual(
            seed.public_view_key(),
            '2fcd275e4337152ea77ac68ec02f166a243f4917ebd53b2a381ab27b84d24065')
        self.assertEqual(
            seed.public_address(),
            '4A5uCL4cXoB9XD3WjTrEwvNBQ6JRPTHaY9uVaxfWmcLy5YkE81tW7B28oc42XGzAeRJkhyHjKAxSE84aZnihjVBVCQf15mw')

    def test_esperanto(self):
        seed = Seed(u"knedi aspekti boli asbesto pterido aparta muro sandalo hufumo porcelana degeli utopia ebono lifto dutaga hundo vejno ebono higieno nikotino orkestro arlekeno insekto jaguaro hundo", "Esperanto")
        self.assertEqual(
            seed.secret_spend_key(),
            'a8e8a30d3638cc4d09d1fa9f4de12ac0096c69a77896774793627c0cc6a28703')
        self.assertEqual(
            seed.secret_view_key(),
            '8b4dcbcbafaf3d195af5bd54aa386d767a8de3b45236c9842cb876212427f103')
        self.assertEqual(
            seed.public_spend_key(),
            '32c8a782c05db039018caa150bef1f66621831b3cb591401381e1dfc3c3d423e')
        self.assertEqual(
            seed.public_view_key(),
            '047963206a0267649657936d268824e35e59e3426c63b9f3b04788b14af1d85f')
        self.assertEqual(
            seed.public_address(),
            '43YjCQcHm8TAY2kKbSMHz6J8FDZQwjPxw1Cq1vQ7SsQVBNeYEUMwGTQHppi5ffwg3df2m56DYexj2hm5uaQDtqpTBnUVzmD')

    def test_french(self):
        seed = Seed(u"sauce exprimer chasse asile larve tacler digestion muguet rondeur sept clore narrer fluor arme torse dans glace tant salon sanguin globe quiche ficher flaque clore", "French")
        self.assertEqual(
            seed.secret_spend_key(),
            '597703dd73d0da6b3996b83c3e1e2f602be4f0de453e15846171aa9076901603')
        self.assertEqual(
            seed.secret_view_key(),
            'f6e448dbbeaa7682a541b3b5b7e2e8ebb614fac032f1c3dff659ca26ab430f09')
        self.assertEqual(
            seed.public_spend_key(),
            '10b42e100196ef2a68eeec191a46d8dc5c83d73c0861c185e5244202cd432087')
        self.assertEqual(
            seed.public_view_key(),
            '34c4c479d53b10d3e9c0a3d11432fd13611b12dc5b721c8ff3802329b7bac328')
        self.assertEqual(
            seed.public_address(),
            '42FpfU7DfLi86RtY3ajKUKdrnKvXTx41WPPx6wsyp9XVPcfnrLDXxhucSphpzt3mDv4F1DMiCrfHmR5WPZq1erzn5bs4eA7')

    def test_german(self):
        seed = Seed(u"Erdgas Gesuch beeilen Chiffon Abendrot Alter Helium Salz Almweide Ampel Dichter Rotglut Dialekt Akkord Rampe Gesöff Ziege Boykott keuchen Krach Anbau Labor Esel Ferien Ampel", "German")
        self.assertEqual(
            seed.secret_spend_key(),
            '193152abe15c5e0a0ff56e3020229398769cd7c6ca5a4e30e439d6702c4f320a')
        self.assertEqual(
            seed.secret_view_key(),
            'cdb967c501195827d78a791e1173d4b8826a5ae73b0885984898c84b6c9dd80c')
        self.assertEqual(
            seed.public_spend_key(),
            '32eac115ca4b072c18198966c7ac9cb63b9f701a691eb52bfa18345d0fbcd90f')
        self.assertEqual(
            seed.public_view_key(),
            '06a2119dfa7c48bdc03ad251026fc509bd01f3a4f7521802ca31b93cf06539ac')
        self.assertEqual(
            seed.public_address(),
            '43Z2BHsCkU68NmZrxzfZuuXUtUHCXWttt8MdcnNyDMkC3WmfoFb9byqYjpeBaC4Xtx2dUUv8YPv1d1U4krZCLzyWLUFif2E')

    def test_italian(self):
        seed = Seed(u"tramonto spuntare ruota afrodite binocolo riferire moneta assalire tuta firmare malattia flagello paradiso tacere sindrome spuntare sogliola volare follia versare insulto diagnosi lapide meteo malattia", "Italian")
        self.assertEqual(
            seed.secret_spend_key(),
            '29c8d9e91c1cb59e059bddd901e011db85f8d4f00f967226ffb5e185bd10e70d')
        self.assertEqual(
            seed.secret_view_key(),
            '1f224a0330ee358428fe91fa48b6986941030c34f2d1efecc4eb26ea9f838b02')
        self.assertEqual(
            seed.public_spend_key(),
            '149bdad48fd1ca40e1eb3e323b676132e2cae1eedbd715ac131b97c2c749c6b4')
        self.assertEqual(
            seed.public_view_key(),
            'efc1a3382c33ac58ecfdd3a71497b0d0aeef061d0af94e5c49278d653167d643')
        self.assertEqual(
            seed.public_address(),
            '42QQUPDR9PoBrSc9rB5VvG9Wf7KmtjXhEVnLhGKif9rDXGK3n1e6rsVFsh62YDqDf5buVQXuL6oLHGSHg4ANgQUu8beDd9R')

    def test_japanese(self):
        seed = Seed(u"いもり すあな いきる しちょう うったえる ちひょう けなみ たいちょう うぶごえ しかい しなぎれ いっせい つかれる しなん ばあさん たいまつばな しひょう おいかける あんがい ていへん せんもん きこく せんく そそぐ つかれる", "Japanese")
        self.assertFalse(seed.is_mymonero())
        self.assertEqual(
            seed.secret_spend_key(),
            'a047598095d2ada065af73758f7082900b9b0d721b5f99a541a78bd461ffc607')
        self.assertEqual(
            seed.secret_view_key(),
            '080c6135edf93233176d41c8535caef0f13d596dc5093b5a5afa4279339dbc00')
        self.assertEqual(
            seed.public_spend_key(),
            '85d849793fce4d0238d991d3aab7ac790cee73e5732d378c216f11bd3b873e43')
        self.assertEqual(
            seed.public_view_key(),
            '19dc462a6074a26fa7788b45e542a71ffdbd48502e41ae8790c46fd6de556de3')
        self.assertEqual(
            seed.public_address(),
            '46hHs9s3boi1NZJHGSwMgfMFLpCBaKwdQQSSf7fqVjWdCDxudsDmqqbKgBkpYDX6JA6MMZG8o5yrMPg9ztrXHdEkSfUA131')

    def test_portuguese(self):
        seed = Seed(u"rebuscar mefistofelico luto isca vulva ontologico autuar epiteto jarro invulneravel inquisitorial vietnamita voile potro mamute giroscopio scherzo cheroqui gueto loquaz fissurar fazer violoncelo viquingue vulva", "Portuguese")
        self.assertFalse(seed.is_mymonero())
        self.assertEqual(
            seed.secret_spend_key(),
            '60916cfcb10fa0b2b0648e36ecd7037f5c1972d36b2e6d56c2f4feca613a4200')
        self.assertEqual(
            seed.secret_view_key(),
            'b23941e3f4da76e0fab171d94a36fe70031fb501f1f80e0cb3b4b4638b5f7106')
        self.assertEqual(
            seed.public_spend_key(),
            '340c89026a03637e8b0abda566ac99b98a7c85b30a81281be19af869c3631dfb')
        self.assertEqual(
            seed.public_view_key(),
            '23bb38c5e34867c49a65f0e7192138483361d419febbd429f256088e5e62a55e')
        self.assertEqual(
            seed.public_address(),
            '43bWUqKAoYWNAdMtuaSF2pY2yptw7zfCB5fV2fXLkYTvj1NNYUKM4aaZtJCVYJunHuD5SNE2CPTCo81wDhZc8bReBidbX1w')

    def test_russian(self):
        seed = Seed(u"дощатый ателье мыло паек азот ружье домашний уныние уплата торговля шкаф кекс газета тревога улица армия лазерный иголка друг хищник пашня дневник кричать лыжный иголка", "Russian")
        self.assertEqual(
            seed.secret_spend_key(),
            '6dc31f6ebcf834ab375a69006cb19c66fcccfa0732dfb3ea1b0662b455226b0d')
        self.assertEqual(
            seed.secret_view_key(),
            '5467825ef0148a11582115f80b01c9af90fe31216a9cf6fb2d6b3c78698ce80a')
        self.assertEqual(
            seed.public_spend_key(),
            '200657c6d14ab19cd3fccd8634e8f23e81290a559b8eb5e58dda3696553ddffc')
        self.assertEqual(
            seed.public_view_key(),
            'f7563d9efb1c03a299b9c91a604caf7fd0c5a6998fdeedf18b58a63930958a24')
        self.assertEqual(
            seed.public_address(),
            '42qVnaWnHSGTERsT6diSvdBTNbHfQZauSfPxpc5EuHc2jK699E28uwpUCRrHr9aaZ4NNyJ9ABdxX6hQHPHv2YcW55A26UbQ')

    def test_spanish(self):
        seed = Seed(u"riesgo lápiz martes fuerza dinero pupila pago mensaje guion libro órgano juntar imperio puñal historia pasión nación posible paso límite don afirmar receta reposo fuerza", "Spanish")
        self.assertFalse(seed.is_mymonero())
        self.assertEqual(
            seed.secret_spend_key(),
            '5973d91299466a9a51ddfcd20d1710c776aa1399279b292b264ab6b7ab608105')
        self.assertEqual(
            seed.secret_view_key(),
            '5f7a66cf32120515870f89e3a156ec2024154334a3b43af1da05244ec4cf250d')
        self.assertEqual(
            seed.public_spend_key(),
            '42161417635c6bd31a8dce8c2bd3b5f4879369fb732073d9f6fa82b18329c7f7')
        self.assertEqual(
            seed.public_view_key(),
            '6acc984fecb5894b5661d446954ffcfe302cd1d2cf0e5177c2553aafb1dc3d2a')
        self.assertEqual(
            seed.public_address(),
            '448MxehQwbgcJyJ3fKnTYYhuF7g7cs7AJdTXoybMu8UEiPFtFpEVNTaDbsK5vatPHVjWwjvJfyWKiM2pBKXJrg4U5qeGXjZ')


if __name__ == "__main__":
    unittest.main()
