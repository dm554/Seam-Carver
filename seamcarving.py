#import numpy as np
import sys
import math
#from matplotlib.pyplot import imshow
#from matplotlib.pyplot import show
from PIL import Image

def FormatFilename(inputFileName, nameAppend) :
    imgInfo = inputFileName.split('/')[-1].split('.')
    imageName = imgInfo[0]
    extension = "." + imgInfo[1]
    return imageName + nameAppend + extension

def GreyScale(image) : 
    greyImage = Image.new('RGB', (image.width, image.height), 'black')
    pix = image.load()
    pixelGrey = greyImage.load()
    gray = [0.3 ,0.59, 0.11]
    for x in range(0, image.width - 1):
        for y in range(0, image.height - 1):
            gray = int(0.3 * pix[x,y][0] + 0.59 * pix[x,y][1] + 0.11 * pix[x,y][2])
            pixelGrey[x,y] = (gray, gray, gray)
    return greyImage


def SobelImage(image, matrix) : 
    sobelImg = Image.new('RGB', (image.width, image.height), 'white')
    pixels = image.load()
    pixSobel = sobelImg.load()
    for x in range(0, image.width):
        for y in range(0, image.height):
            sumval = 0
            for i in range(0, len(matrix)):
                try:      
                    if (i == 0):
                        sumval += matrix[i] * pixels[(x-1),(y+1)][0]
                    elif(i == 1):
                        sumval += matrix[i] * pixels[x,(y+1)][0]
                    elif(i == 2):
                        sumval += matrix[i] * pixels[(x+1),(y+1)][0]
                    elif(i == 3):
                        sumval += matrix[i] * pixels[(x-1),y][0]
                    elif(i == 4):
                        sumval += matrix[i] * pixels[x,y][0]
                    elif(i == 5):
                        sumval += matrix[i] * pixels[(x+1),y][0]
                    elif(i == 6):
                        sumval += matrix[i] * pixels[(x-1),(y-1)][0]
                    elif(i == 7):
                        sumval += matrix[i] * pixels[x,(y-1)][0]
                    elif(i == 8):
                        sumval += matrix[i] * pixels[(x+1),(y-1)][0]
                except IndexError:
                    pass
            if (abs(sumval) > 255):
                sumval = 255
            sumval = abs(sumval)
            pixSobel[x,y] = (sumval, sumval, sumval)
            pass # TODO find pixSobel[x,y] 
    #sobelImg.show()
    return sobelImg

def GradientImage(imageX, imageY):
    gradientImg = Image.new('RGB', (imageX.width, imageX.height), 'white')
    pixSobX = imageX.load()
    pixSobY = imageY.load()
    gradientPix = gradientImg.load()
    for x in range(0, imageX.width):
        for y in range(0, imageX.height):
            gradient = int(math.sqrt( (math.pow(pixSobX[x,y][0], 2) + math.pow(pixSobY[x,y][0], 2)) ) )
            gradientPix[x,y] = (gradient, gradient, gradient)
    #gradientImg.show()
    return gradientImg

def CreateCostMatrix(energyMap) :
    costMatrix = [[0]*energyMap.width for _ in range(energyMap.height)] 
    #np.empty((energyMap.width, energyMap.height), int)
    pixels = energyMap.load()
    count = 0
    for y in range(0, energyMap.height): #We do y first to iterate by rows
        for x in range(0, energyMap.width):
            ep = []
            if((y+1) < energyMap.height):
                if ((x - 1) > 0):
                    ep.append(pixels[(x-1), (y+1)][0])
                if((x+1) < energyMap.width):
                    ep.append(pixels[(x+1), (y+1)][0])
                ep.append(pixels[x, (y+1)][0])
            try:
                ev=pixels[x,y][0] + min(ep)
            except ValueError:
                break
            #np.insert(costMatrix, [x-1], ev, axis=1)
            costMatrix[y][x] = ev
            count += 1
            #print("insert worked: %s %s" % (count, ev) )
            pass # TODO find costMatrix[x,y]
    #print(costMatrix)   
    return costMatrix

def FindSeam(costMatrix) : 
    height = len(costMatrix) - 1
    width = len(costMatrix[0]) - 1
    startPix = min(costMatrix[0])
    startIndex = costMatrix[0].index(startPix)
    seamToRemove = [startIndex]
    
    for y in range(0, (height)): #We do y first to iterate by rows
        currentPix = seamToRemove[-1]
        currentPix3 = [costMatrix[y + 1][currentPix - 1], costMatrix[y + 1][currentPix],costMatrix[y + 1][currentPix + 1]]
        eMin = currentPix3.index(min(currentPix3))
        posdict = {
            0: currentPix - 1,
            1: currentPix,
            2: currentPix + 1
        }
        seamToRemove.append(posdict[eMin])
    #print(seamToRemove)
    # TODO find the seam to remove 
    return seamToRemove

def RemoveSeam(image, imageGrad, seam) : 
    newImg = Image.new('RGB', (image.width-1, image.height), 'black')
    newGrad = Image.new('RGB', (image.width-1, image.height), 'black')
    
    oI = image.load()
    nI = newImg.load()
    oG = imageGrad.load()
    nG = newGrad.load()
    subVar = 1
    # TODO Remove the seam from the image
    #iterate through seam and remove pixels
    for y in range(image.height):
        subVar = 1
        for x in range(image.width-subVar):
            if(x == seam[y]):
                subVar = 2
                
            nI[x,y] = oI[(x + subVar - 1),y]
            nG[x,y] = oG[(x + subVar - 1),y] 

    return [newImg, newGrad]


if len(sys.argv) <= 1 :
    print("No argument provided")
    exit()

try :
    originalImg = Image.open(sys.argv[1], "r")
except FileNotFoundError :
    print("Input file could not be found.")
    exit()
except Image.UnidentifiedImageError : 
    print("Not a valid image input")
    exit()

try : 
    newWidth = int(sys.argv[2])
except ValueError : 
    print("2nd Argument must be a int value")
    exit()

originalImg = originalImg.convert("RGB")
newImage = originalImg
sobleX = [ -1, 0, 1, -2, 0, 2, -1, 0, 1 ]
sobleY = [ -1, -2, -1, 0, 0, 0, 1, 2, 1 ]

seamsRemain = originalImg.width - newWidth
print("Seams remaining:", seamsRemain, ' ' * 10, end='\r', flush=True)
#these calculations only need to happen once
greyImg = GreyScale(newImage)
sobelImgX = SobelImage(greyImg, sobleX)
sobelImgY = SobelImage(greyImg, sobleY)
gradImg = GradientImage(sobelImgX, sobelImgY)

while newWidth < newImage.width :

    costMatrix = CreateCostMatrix(gradImg)
    seam = FindSeam(costMatrix)
    seamedImages = RemoveSeam(newImage, gradImg, seam)
    #newImage = RemoveSeam(newImage, seam)
    #sobelImgX = RemoveSeam(sobelImgX, seam)
    #sobelImgY = RemoveSeam(sobelImgY, seam)
    #gradImg = RemoveSeam(gradImg, seam)
    newImage = seamedImages[0]
    gradImg = seamedImages[1]

    #Friendly output to tell the user how many more seams need to be done
    seamsRemain-=1
    print("Seams remaining:", seamsRemain, ' ' * 10, end='\r', flush=True)
    
sys.stdout.write('\x1b[2K')
fileName = FormatFilename(sys.argv[1], "_Seamed")
newImage.save(fileName)