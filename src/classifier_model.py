import torch
from torchvision.models import resnet50, ResNet50_Weights


class Trash:
    def __init__(self):

        self.weights = ResNet50_Weights.DEFAULT
        self.model = resnet50(weights=self.weights)
        self.classes = ['barn', 'bell cote', 'birdhouse', 'boathouse', 'bow', 'briard', 'castle', 'church', 'cinema',
                        'convertible',
                        'dome', 'fire screen', 'fountain', 'greenhouse', 'hamper', 'lakeside', 'library', 'maze',
                        'mobile home', 'monastery',
                        'palace', 'patio', 'picket fence', 'planetarium', 'prison', 'scoreboard', 'shoji',
                        'sliding door',
                        'solar dish',
                        'thatch', 'tile roof', 'tub', 'vault', 'web site', 'window screen', 'window shade',
                        'worm fence']
        self.preprocess = self.weights.transforms()

    def prediction(self, image) -> str:
        self.model.eval()
        batch = self.preprocess(image).unsqueeze(0)
        prediction = self.model(batch).squeeze(0).softmax(0)
        class_id = prediction.argmax().item()
        return self.weights.meta["categories"][class_id]

    def __call__(self, image) -> bool:
        image = torch.from_numpy(image)
        if self.prediction(image) in self.classes:
            return True
        else:
            return False
