'''
void CLoadCoeffDlg::ProgramStage(int nStage)
{
   BYTE WE;
   BYTE WritePort[4];
   BYTE WriteData[4];
   int nTotal;
   if(nStage==0){   //programming stage 1
        WE=0x10;
        WritePort[0]=41;
        WritePort[1]=40;
        WritePort[2]=39;
        WritePort[3]=38;
        nTotal=64;
    } else{ //programming stage 2
        WE=0x01;
        WritePort[0]=45;
        WritePort[1]=44;
        WritePort[2]=43;
        WritePort[3]=42;
        nTotal=16
    }

    if(!m_pParent->WriteRegisters(1, 37, &WE))
       return;
    for(int nCIndex=0; nCIndex<nTotal; nCIndex++){
       for(int nCh=0; nCh<8; nCh++){
            DWORD nCoeff;
            if(nStage==0)
                nCoeff=CoeffCh[nCh].CoeffStage1[nCIndex];
            else
                nCoeff=CoeffCh[nCh].CoeffStage2[nCIndex];
            WriteData[0]=(BYTE)(nCoeff>>24)&0xff;
            WriteData[1]=(BYTE)((nCoeff>>16)&0xff);
            WriteData[2]=(BYTE)((nCoeff>>8)&0xff);
            WriteData[3]=(BYTE)((nCoeff)&0xff);
            if(!m_pParent->WriteRegisters(4, WritePort, WriteData))
                return;
        }
    }
    WE=0x00;
    if(nStage == 0) WriteRegisters(1, 38, &WE);
    else if(nStage == 1) WriteRegisters(1, 42, &WE);
    if(!m_pParent->WriteRegisters(1, 37, &WE));
}
'''
import smbus
import coeff
import struct
import float2int
import sys
''' use ES9018 internal programable FIR filter as crossover
    =====================================================
    Channel maps for stereo 2 way crossover:
    left channel -> {0(low), 2(high)}, {4(low), 6(high)}
    right channel -> {1(low), 3(high)}, {5(low), 7(high)}
    =====================================================
    we only enable stage 1
'''
if len(sys.argv) != 2:
    print('This command supports only one parameter: sample rate =("96k", "44k1", "48k")')
    quit()
if sys.argv[1] == '96k':
    lowpass_coeff = coeff.lp_96k
    highpass_coeff = coeff.hp_96k
elif sys.argv[1] == '48k':
    lowpass_coeff = coeff.lp_48k
    highpass_coeff = coeff.hp_48k
elif sys.argv[1] == '44k1':
    lowpass_coeff = coeff.lp_44k1
    highpass_coeff = coeff.hp_44k1
else:
    print(f'Unsupported sample rate: \'{sys.argv[1]}\'')
    quit()
i2c = smbus.SMBus(1)
i2c.write_byte_data(0x49, 37, 0x10)
for idx in range(64):
    for i in range(8):
        if i in (0, 2, 4, 6):  # this is low pass filter, for testing
            # if i in (0, 1, 4, 5):  this is real mapping
            coeff_value = lowpass_coeff[idx]
        else:
            coeff_value = highpass_coeff[idx]
        if coeff_value < 0:
            coeff_value = -coeff_value
            sign_flag = 1
        else:
            sign_flag = 0
        value32 = list(struct.pack('<i', float2int.f2i(coeff_value)))
        for j in range(3, -1, -1):
            i2c.write_byte_data(0x49, 38 + j, value32[j])
i2c.write_byte_data(0x49, 38, 0)
i2c.write_byte_data(0x49, 37, 0)
i2c.write_byte_data(0x49, 37, 0x20)
