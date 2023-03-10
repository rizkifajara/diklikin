USE heroku_e0f5c6fd211d61f;
CREATE TABLE `products` (
  `productId` varchar(15) NOT NULL,
  `productName` varchar(150) NOT NULL,
  `productDescription` text NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `category` varchar(30) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `img` varchar(200) NOT NULL,
  `sellerId` int NOT NULL DEFAULT '1',
  `inputDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`productId`),
  KEY `sellerId_idx` (`sellerId`),
  KEY `seller_idx` (`sellerId`),
  CONSTRAINT `seller` FOREIGN KEY (`sellerId`) REFERENCES `users` (`userId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

insert into `products` (`productId`,`productName`,`productDescription`,`price`,`category`,`img`,`sellerId`,`inputDate`) values
('T02_1093','Kanoodle 3-D Brain Teaser Puzzle Game','Can you Kanoodle? Using combinations of colored connected beads, players complete colorful puzzles in two unique formats: tricky 2D puzzles and twisted 3D pyramids. To start, pick a design from the puzzle book, place some of the puzzle pieces into position as shown…then fill the empty spaces with the remaining pieces.',
'205000','Games','https://m.media-amazon.com/images/I/71WXg65OaLL._AC_SL1500_.jpg',1,'2020-01-01'),
('K10_2308','Dash Mini Waffle Maker Machine for Individuals','Craving blueberry waffles or potato pancakes? with the Dash mini waffle maker, you can make single serve dishes in less than three minutes. The nonstick surface allows you to perfectly cook and Brown whatever is it you make, and is a fun activity for both adults and kids! ',
'264000','Applicances','https://m.media-amazon.com/images/I/81G0GtFE3TL._AC_SL1500_.jpg',11,'2019-11-23'),
('O34_1023','Philips Sonicare HX9690/05 ExpertClean 7500 Bluetooth Rechargeable Electric Power Toothbrush','Everything you need for great oral health. Philips Sonicare Expert Clean 7500 will guide you between dentist checkups and you will experience improved oral health with up to 10x more plaque removal vs. a manual toothbrush. With a built-in pressure sensor and the smart sensor progress report, the power toothbrush has everything you need to guide you into better oral health care habits starting day one.',
'2000000','OralCare','https://m.media-amazon.com/images/I/81U-eoBkhnL._SL1500_.jpg',12,'2021-01-23'),
('H20_2008','Jabra Elite Active 75t True Wireless Bluetooth Earbuds','Jabra Elite Active 75t true wireless earbuds are engineered for secure fit and designed for running and exercise, with a special grip coating which allows the earbuds to stay firmly in place, even when you really put them through their paces. Waterproof with IP57-rated durability. With a battery life of up to 7.5 hours.',
'2600000','Headphones','https://m.media-amazon.com/images/I/71dajYuJBjL._AC_SL1500_.jpg',9,'2020-08-20'),
('S22_2023','TruSkin Vitamin C Serum for Face','Vitamin C blends with Botanical Hyaluronic Acid, Vitamin E, Witch Hazel, and Jojoba Oil in an anti aging, skin brightening formula designed to improve wrinkles and dark spots',
'476000','SkinCare','https://m.media-amazon.com/images/I/61zI9U6HBLS._SL1500_.jpg',16,'2022-02-23'), 
('T10_1648','Monopoly Game of Thrones Board Game for Adults','Game of Thrones meets the Fast-Dealing Property Trading Game in this Monopoly game for GOT fans. The gameboard, packaging, tokens, money, Chance cards, and game pieces are all inspired by the popular TV series from HBO',
'470000','Games','https://m.media-amazon.com/images/I/91eA8-TC0VL._AC_SL1500_.jpg',1,'2018-12-11'), 
('A09_6002','iOttie Easy One Touch 4 Dash & Windshield Universal Car Mount Phone Holder Desk Stand','The iOttie Easy One Touch 4 Dashboard & Windshield Mount is a universal smartphone solution that is engineered to safely enhance your driving experience. U.S. patent protected, the one of a kind easy one touch mechanism allows you to easily mount and remove your smartphone with one simple hand motion.',
'347000','Accessories','https://m.media-amazon.com/images/I/718NVofDrCL._AC_SL1500_.jpg',15,'2020-09-06'),
('V21_1840','BLACK+DECKER 20V Max Handheld Vacuum','Equipped functional features with a 200° pivoting nozzle, an extendible crevice tool, and a large, easy-to-empty dirt bowl, the cordless handheld PIVOT VAC powerfully cleans those hard-to-reach spaces.',
'1015000','Vacuums','https://m.media-amazon.com/images/I/516LsONVRuS._AC_SL1000_.jpg',13,'2021-04-18'),
('C22_2006','Cleaning Gel for Car','Car interior cleaner can perfectly clean the dust, debris and soot in the narrow gap. Just take out the cleaning gel, knead it in your hand, and then place it in a dusty place and gently squeeze our car cleaner to get a perfect cleaning effect',
'103000','CarCare','https://m.media-amazon.com/images/I/71YLxhnPUxL._AC_SL1500_.jpg',11,'2020-06-22'),
('K07_3020','Dash Mini Rice Cooker Steamer','A small and mighty appliance, perfectly portioned for meals and meal preparation, the Dash Mini Rice Cooker is the one pot to cook it all and more. Featuring a keep warm function, you can keep your meal and ingredients hot for a longer time',
'367000','Applicances','https://m.media-amazon.com/images/I/61sOcTFhudL._AC_SL1500_.jpg',11,'2021-07-30'),
('V19_2820','Brigii 3-in-1 Handheld Vacuum Cleaner','Compact and powerful suction: The light weight vacuum cleaner weighs just 485g, and it has built-in our unique air-duct technology provided powerful suction.',
'854000','Vacuums','https://m.media-amazon.com/images/I/51whI-1wAAL._AC_SL1500_.jpg',13,'2019-02-28'),
('V17_1320','Moyidea Handheld Vacuum','Rechargeable Cordless Vacuum, the Best & Smart Choice for Pet Hair, Car and Home Cleaning',
'515000','Vacuums','https://m.media-amazon.com/images/I/7164GmM4F1L._AC_SL1500_.jpg',13,'2017-03-12'),
('A11_2621','LISEN Cell Phone Stand','Lisen 2021 upgraded phone stand features all metal rod and weighted base, which improves 3x stability and solves the common falling off problem',
'245000','Accessories','https://m.media-amazon.com/images/I/61vOaXrPL2L._AC_SL1400_.jpg',8,'2021-11-26'),
('O21_7090','BTFO Sonic Electric Toothbrush with 5 Modes','The sonic electric toothbrush has high quality, which can provide long service life. Soft brush head, smooth and sturdy toothbrush host can bring better use experience for you.',
'338900','OralCare','https://m.media-amazon.com/images/I/71Rs0bWw6dL._AC_SL1500_.jpg',16,'2021-07-09'),
('H20_1504','Srhythm NC15 Noise Cancelling Headphones','World-leading Noise Cancellation Technology: Effectively quell 85% background noise, helps you to remove unwanted sounds, lets you block out the world around you to enjoy your music or the sweet sound of silence.',
'736500','Headphones','https://m.media-amazon.com/images/I/71Px9XZZbuL._AC_SL1500_.jpg',10,'2020-04-20'),
('S18_1005','Hyaluronic Acid Serum for Skin','Improve skin texture and brightness with intense moisture and balance. Hydrating facial moisturizer with 100 percent pure hyaluronic acid serum formula.',
'191600','SkinCare','https://m.media-amazon.com/images/I/41K+rk3HgcL.jpg',16,'2018-05-10'),
('C18_1907','MYCHANIC Rolling Car Wash Stool','Our Rolling Car Wash Stool features an integrated bucket dolly, cup holder, bottle racks, and a storage tray for loose tools and hardware. Now your next detailing project doesn’t have to become a devil of a job.',
'2500000','CarCare','https://m.media-amazon.com/images/I/71NgUo3nmVL._AC_SL1500_.jpg',14,'2018-07-19');


INSERT INTO `users`
(`userId`,
`name`,
`email`,
`username`,
`password`,
`mobileNo`)
VALUES
(8,'Lisen','lisen@gmail.com','Lisen Store','Lisen','08221341994'),
(9,'Jabra','jabra@gmail.com','Jabra Store','Jabra','08111347694'),
(10,'Srhythm','srhythm@gmail.com','Srhythm Store','Srhythm','0823461923'),
(11,'DASH','dash@gmail.com','DASH Store','DASH','08276481994'),
(12,'Philips','philips@gmail.com','Philips Store','Philips','08220211954'),
(13,'Black+ Decker','decker@gmail.com','BLACK+ DECKER Store','Decker','0822125795'),
(14,'Mychanic','mychanic@gmail.com','Mychanic Store','Mychanic','08231212355'),
(15,'iOttie','iottie@gmail.com','iOttie Store','iOttie','08220189004'),
(16,'Truskin','truskin@gmail.com','Truskin Store','Truskin','0831129004');
