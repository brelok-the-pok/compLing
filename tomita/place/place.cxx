#encoding "utf-8"
#GRAMMAR_ROOT S

Mamaev -> Word<wff="[Мм]амае[а-я]*"> Word<wff="[Кк]урган[а-я]*">;
Avangard -> Word<wff="[Аа]вангард[а-я]*">;

//Gorkiy -> Word<wff="М. Горького">;// | Word<wff="М.Горького">;

SomePlace -> Word<wff="[Бб]иблиотек[а-я]*"> | Word<wff="[Пп]арк[а-я]*"> | Word<wff="[Пп]лощад[а-я]*">;

PlaceSomeName -> SomePlace Word<wff="им[а-я.]*"> Word Word;

Square -> Word<wff="[Пп]лощад[а-я]*"> Word<wff="[Пп]авших"> Word<wff="[Бб]орцов">;

Phihlip ->Word<wff="[Сс]аш[а-я]*"> Word<wff="[Фф]и[л]*и[п]*ов[а-я]*">;

Museum -> Word<wff="[Мм]узе[а-яА-Я-]*">;

OneWord -> Word;
TwoWords -> Word Word;
ThreeWords -> Word Word Word;
FourWords -> Word Word Word Word;
FiveWords -> Word Word Word Word Word;

UpToFiveWords -> OneWord | TwoWords | ThreeWords | FourWords| FiveWords; 
SomeMuseum -> Museum UpToFiveWords;

Memorial -> Word<wff="[Пп]амятник[а-я]*">;

Chekisty -> Memorial Word<wff="[Чч]екист[а-я]*">;

Dzerzhinsky -> Memorial Word<wff="[Дд]зержинск[а-я]*">;

Church -> Word<wff="[Цц]ерк[а-я]*"> Word<wff="[Сс]вято[а-я]*"> Word<wff="[Гг]еорг[а-я]*">;

Train -> Word<wff="[Тт]рамва[а-я-]*">;

Echelon -> Word<wff="[Вв]оинск[а-я]*"> Word<wff="[Ээ]шелон[а-я-]*">;

Mill -> Word<wff="[Мм]ельниц[а-я]*"> Word<wff="[Гг]ергардт[а-я-]*">;

FireMan -> Word<wff="[Зз]дан[а-я]*"> Word<wff="[Цц]арицынск[а-я]*"> Word<wff="[Пп]ожарн[а-я]*"> Word<wff="[Кк]оманд[а-я]*">;

Pavlov -> Word<wff="[Дд]ом[а-я]*"> Word<wff="[Пп]авлов[а-я]*">;

Chelyb ->  Word<wff="[Чч]еляб[а-я]*"> Word<wff="[Кк]олхоз[а-я]*">;

Gogol -> Memorial Word<wff="[Гг]огол[а-я]*">;
BK -> Word<wff="[Бб][Кк]-13*">;
Synagogue -> Word<wff="[Cc]инагог[а-я]*"> Word<wff="[Бб]ейт[а-я]*"> Word<wff="[Дд]авид[а-я]*">;

Fountain -> Word<wff="[Фф]онтан[а-я]*">;

BarmFount -> Fountain Word<wff="[Бб]армал[а-я]*">;

LoversFount -> Fountain Word<wff="[Вв]любл[а-я]*">;

Mount -> Word<wff="[Лл]ыс[а-я]*"> Word<wff="[Гг]ор[а-я]*">;

Panikaha -> Memorial Word<wff="[Пп]аниках[а-я]*">;

Elevator -> Word<wff="[Ээ]леватор[а-я]*">;

Cathedral -> Word<wff="[Кк]азанск[а-я]*"> Word<wff="[Кк]афедр[а-я]*"> Word<wff="[Сс]обор[а-я]*">;

Port -> Word<wff="[Рр]ечн[а-я]*"> Word<wff="[Пп]орт[а-я]*">;

Opera -> Word<wff="[Цц]арицын[а-я]*"> Word<wff="[Оо]пер[а-я]*">;

Park -> Word<wff="[Пп]арк[а-я]*">;

WinPark -> Park Word<wff="[Пп]обед[а-я]*">;

Comsomol -> Word<wff="[Кк]омсомол[а-я]*"> Park;

ChildPark -> Word<wff="[Дд]етск[а-я]*"> Word<wff="[Гг]оород[а-я]*"> Park;

FriendshipPark -> Park Word<wff="[Дд]ружб[а-я]*">;

Glory -> Word<wff="[Зз]ал[а-я]*"> Word<wff="[Вв]оинск[а-я]*"> Word<wff="[Сс]лав[а-я]*">;

Botan -> Word<wff="[Бб]отан[а-я]*"> Word<wff="[Сс]ад[а-я]*">;

CentParkFull -> Word<wff="[Цц]ентраль[а-я]*"> Park UpToFiveWords;
CentParkSmall -> Word<wff="ЦПК[Ии]О">;
CentPark -> CentParkFull | CentParkSmall;

Planet -> Word<wff="[Пп]ланетар[а-я]*">;

Filarm -> Word<wff="[Вв]олгог[а-я]*"> Word<wff="[Оо]блас[а-я]*"> Word<wff="[Фф]иларм[а-я]*">;

Arena -> Word<wff="[Вв]олгог[а-я]*">  Word<wff="[Аа]рен[а-я]*">;

Places -> Mamaev | Avangard | PlaceSomeName | Square | Phihlip| Dzerzhinsky | SomeMuseum | Chekisty | Church | Train| Echelon | Mill | FireMan | Pavlov | Chelyb | Gogol | BK| Synagogue | BarmFount | LoversFount | Mount | Panikaha | Elevator | Cathedral | Port | Opera | WinPark | Arena |Filarm |Planet|CentPark|Botan|FriendshipPark|ChildPark|Comsomol|WinPark;

S -> Places interp (Place.Name);



















