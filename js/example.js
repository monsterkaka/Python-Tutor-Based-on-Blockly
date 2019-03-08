var example ='<xml xmlns="http://www.w3.org/1999/xhtml">\
  <variables>\
    <variable type="" id=")c}P(`BMXDuFi;*_E@@$">t</variable>\
    <variable type="" id="Zq^k3oEZ=;$=$VbJ9wYd">i</variable>\
    <variable type="" id="Fb5m7[,,W^.q(yagh`vz">index</variable>\
    <variable type="" id="UH{{bAsQ@24VpE3`6Vrm">j</variable>\
    <variable type="" id="bDlFMWR!F[zuUL{5XwGK">temp</variable>\
  </variables>\
  <block type="variables_set" id="1C!{Kki{vdZ8btt{n]NI" x="63" y="63">\
    <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
    <value name="VALUE">\
      <block type="lists_create_with" id="~,:Nu,..vXcR7Lq?^af)">\
        <mutation items="5"></mutation>\
        <value name="ADD0">\
          <block type="math_number" id="|~yP^HN`z^V}_TNC9%sj">\
            <field name="NUM">4</field>\
          </block>\
        </value>\
        <value name="ADD1">\
          <block type="math_number" id="OEnU=kwMu77wQZxAecP{">\
            <field name="NUM">6</field>\
          </block>\
        </value>\
        <value name="ADD2">\
          <block type="math_number" id="AggWj4e9e/=NHSaQ5OB.">\
            <field name="NUM">1</field>\
          </block>\
        </value>\
        <value name="ADD3">\
          <block type="math_number" id="AuIg`WtwF,V%49Ud{RqJ">\
            <field name="NUM">9</field>\
          </block>\
        </value>\
        <value name="ADD4">\
          <block type="math_number" id=".ChwirahST;JuE;HkRau">\
            <field name="NUM">0</field>\
          </block>\
        </value>\
      </block>\
    </value>\
    <next>\
      <block type="variables_set" id="7oi0yotOpjP8HgH6TL^9">\
        <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
        <value name="VALUE">\
          <block type="math_number" id="[pItjrR32Ybjr^+a,h)|">\
            <field name="NUM">1</field>\
          </block>\
        </value>\
        <next>\
          <block type="controls_repeat_ext" id="z[v*!ls`{]5~.p%BioFm">\
            <value name="TIMES">\
              <shadow type="math_number" id=":L(CLE8chj3drl5GbcSw">\
                <field name="NUM">10</field>\
              </shadow>\
              <block type="math_arithmetic" id="fkk:!,@KC%V=JB/HH3!B">\
                <field name="OP">MINUS</field>\
                <value name="A">\
                  <shadow type="math_number" id="Bd`J,ViRzP2P.}81%g7J">\
                    <field name="NUM">1</field>\
                  </shadow>\
                  <block type="lists_length" id="7qQ)]@T)A9Xfy6X[^w:$">\
                    <value name="VALUE">\
                      <block type="variables_get" id="~!}dBnCkHs;@n]0{28H5">\
                        <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                      </block>\
                    </value>\
                  </block>\
                </value>\
                <value name="B">\
                  <shadow type="math_number" id="$^yHM@vmY-x9Dx2$#dJ]">\
                    <field name="NUM">1</field>\
                  </shadow>\
                </value>\
              </block>\
            </value>\
            <statement name="DO">\
              <block type="variables_set" id="hh=W_uxlEDl}`W]##pFC">\
                <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                <value name="VALUE">\
                  <block type="variables_get" id="v;2=R7a:$UUU8A3;PQu/">\
                    <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                  </block>\
                </value>\
                <next>\
                  <block type="variables_set" id="5G;-S%+=N`$IjGSz)Vt!">\
                    <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                    <value name="VALUE">\
                      <block type="math_arithmetic" id="PD{$$@.Y$Os)2*;Awfy=">\
                        <field name="OP">ADD</field>\
                        <value name="A">\
                          <shadow type="math_number" id="_|925aL}OSs%Yi3?mj#G">\
                            <field name="NUM">1</field>\
                          </shadow>\
                          <block type="variables_get" id="-iy.L}a.,3iq5qiuQ5`R">\
                            <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                          </block>\
                        </value>\
                        <value name="B">\
                          <shadow type="math_number" id="D^B]4tGCg)bpc=1e=q`~">\
                            <field name="NUM">1</field>\
                          </shadow>\
                        </value>\
                      </block>\
                    </value>\
                    <next>\
                      <block type="controls_whileUntil" id="GPM~dJ:*.j,p=S%Lbz{%">\
                        <field name="MODE">WHILE</field>\
                        <value name="BOOL">\
                          <block type="logic_compare" id="mEqC2[p+_34GWrdhsUgd">\
                            <field name="OP">LTE</field>\
                            <value name="A">\
                              <block type="variables_get" id="gP,uGsKo=Tmo5*qzLUM[">\
                                <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                              </block>\
                            </value>\
                            <value name="B">\
                              <block type="lists_length" id="Sfi+ckmk!fJyZYov=xDz">\
                                <value name="VALUE">\
                                  <block type="variables_get" id="6}#j6Yn2Q8NAz:]K=l3I">\
                                    <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                  </block>\
                                </value>\
                              </block>\
                            </value>\
                          </block>\
                        </value>\
                        <statement name="DO">\
                          <block type="controls_if" id="E(l?vTj_CC~wbkjI}Gn*">\
                            <value name="IF0">\
                              <block type="logic_compare" id="%]q/tQ[z?bu{8-:]BJKf">\
                                <field name="OP">LT</field>\
                                <value name="A">\
                                  <block type="lists_getIndex" id="*RiYmS#ZnfV-t*M,uahn">\
                                    <mutation statement="false" at="true"></mutation>\
                                    <field name="MODE">GET</field>\
                                    <field name="WHERE">FROM_START</field>\
                                    <value name="VALUE">\
                                      <block type="variables_get" id="^=)GXHUPIUau!?Og0FYw">\
                                        <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                      </block>\
                                    </value>\
                                    <value name="AT">\
                                      <block type="variables_get" id=";UJP{mP{K7hd=/44wBe5">\
                                        <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                                      </block>\
                                    </value>\
                                  </block>\
                                </value>\
                                <value name="B">\
                                  <block type="lists_getIndex" id="4L3bh2H)C84aOD_S#H;U">\
                                    <mutation statement="false" at="true"></mutation>\
                                    <field name="MODE">GET</field>\
                                    <field name="WHERE">FROM_START</field>\
                                    <value name="VALUE">\
                                      <block type="variables_get" id="4`_A5e-my3^^_:w~K%`V">\
                                        <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                      </block>\
                                    </value>\
                                    <value name="AT">\
                                      <block type="variables_get" id="tk8_2LLG*0.{g;Dn~uUn">\
                                        <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                                      </block>\
                                    </value>\
                                  </block>\
                                </value>\
                              </block>\
                            </value>\
                            <statement name="DO0">\
                              <block type="variables_set" id="f~;#N_X7w;/pnyqpHKGV">\
                                <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                                <value name="VALUE">\
                                  <block type="variables_get" id="47atIc4m-u9P(iHGN8e%">\
                                    <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                                  </block>\
                                </value>\
                              </block>\
                            </statement>\
                            <next>\
                              <block type="variables_set" id="4h/Y_1|^4AtTcS+;Ow6^">\
                                <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                                <value name="VALUE">\
                                  <block type="math_arithmetic" id="|1d7b|D_%F%r8G/7v}*Y">\
                                    <field name="OP">ADD</field>\
                                    <value name="A">\
                                      <shadow type="math_number" id="{6x=rlMq%oNn6L+[^c!X">\
                                        <field name="NUM">1</field>\
                                      </shadow>\
                                      <block type="variables_get" id="*xus0_{y_/.0%ep_7Azs">\
                                        <field name="VAR" id="UH{{bAsQ@24VpE3`6Vrm" variabletype="">j</field>\
                                      </block>\
                                    </value>\
                                    <value name="B">\
                                      <shadow type="math_number" id="ir.Go}pYrio2#KBd):=*">\
                                        <field name="NUM">1</field>\
                                      </shadow>\
                                    </value>\
                                  </block>\
                                </value>\
                              </block>\
                            </next>\
                          </block>\
                        </statement>\
                        <next>\
                          <block type="controls_if" id="qK:eFz7WVIOgnB(l^LT|">\
                            <value name="IF0">\
                              <block type="logic_compare" id="jcR$u%-;@Ceo21Hi.J$B">\
                                <field name="OP">NEQ</field>\
                                <value name="A">\
                                  <block type="variables_get" id="1uNX:c%b@OBnF%P!o~lD">\
                                    <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                                  </block>\
                                </value>\
                                <value name="B">\
                                  <block type="variables_get" id="*g]+`{po}Cz8=PFCTVPf">\
                                    <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                                  </block>\
                                </value>\
                              </block>\
                            </value>\
                            <statement name="DO0">\
                              <block type="variables_set" id="xS53!*G=Rfk$qbOy)Dg/">\
                                <field name="VAR" id="bDlFMWR!F[zuUL{5XwGK" variabletype="">temp</field>\
                                <value name="VALUE">\
                                  <block type="lists_getIndex" id="-2%=43sLg%QAO..cHvh%">\
                                    <mutation statement="false" at="true"></mutation>\
                                    <field name="MODE">GET</field>\
                                    <field name="WHERE">FROM_START</field>\
                                    <value name="VALUE">\
                                      <block type="variables_get" id="Eeix77lNu-heAyPv,/qd">\
                                        <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                      </block>\
                                    </value>\
                                    <value name="AT">\
                                      <block type="variables_get" id="`E]~qSnZN7Lftc%O_/Dc">\
                                        <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                                      </block>\
                                    </value>\
                                  </block>\
                                </value>\
                                <next>\
                                  <block type="lists_setIndex" id="/:Q~1bp^Tof}W_`I~pn}">\
                                    <mutation at="true"></mutation>\
                                    <field name="MODE">SET</field>\
                                    <field name="WHERE">FROM_START</field>\
                                    <value name="LIST">\
                                      <block type="variables_get" id="{=))[_eMLm2A0zsskt*}">\
                                        <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                      </block>\
                                    </value>\
                                    <value name="AT">\
                                      <block type="variables_get" id="R{HJKvM`jT,+GI/`QVQA">\
                                        <field name="VAR" id="Fb5m7[,,W^.q(yagh`vz" variabletype="">index</field>\
                                      </block>\
                                    </value>\
                                    <value name="TO">\
                                      <block type="lists_getIndex" id="G596DH%:ZJAO^t|bhV!4">\
                                        <mutation statement="false" at="true"></mutation>\
                                        <field name="MODE">GET</field>\
                                        <field name="WHERE">FROM_START</field>\
                                        <value name="VALUE">\
                                          <block type="variables_get" id="#KxHvkY:VUT{EN|tt6X3">\
                                            <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                          </block>\
                                        </value>\
                                        <value name="AT">\
                                          <block type="variables_get" id="-+Ef!gArc9@{`%l7@%rX">\
                                            <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                                          </block>\
                                        </value>\
                                      </block>\
                                    </value>\
                                    <next>\
                                      <block type="lists_setIndex" id="WS_euDtSw,2WlC._Adwb">\
                                        <mutation at="true"></mutation>\
                                        <field name="MODE">SET</field>\
                                        <field name="WHERE">FROM_START</field>\
                                        <value name="LIST">\
                                          <block type="variables_get" id="Hu5aa!-+`v6zOvu9jt_c">\
                                            <field name="VAR" id=")c}P(`BMXDuFi;*_E@@$" variabletype="">t</field>\
                                          </block>\
                                        </value>\
                                        <value name="AT">\
                                          <block type="variables_get" id="$`dec#;nHm@Zt=L5ux1u">\
                                            <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                                          </block>\
                                        </value>\
                                        <value name="TO">\
                                          <block type="variables_get" id="rT)qKu4ofloZ:tI%HQ=n">\
                                            <field name="VAR" id="bDlFMWR!F[zuUL{5XwGK" variabletype="">temp</field>\
                                          </block>\
                                        </value>\
                                      </block>\
                                    </next>\
                                  </block>\
                                </next>\
                              </block>\
                            </statement>\
                            <next>\
                              <block type="variables_set" id="vQ*Lx2bzOmiqy1w6r!W:">\
                                <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                                <value name="VALUE">\
                                  <block type="math_arithmetic" id="]E9oI[,SCamn^b--EVEK">\
                                    <field name="OP">ADD</field>\
                                    <value name="A">\
                                      <shadow type="math_number" id="2Q+VD/qrtJpRxn[l_viy">\
                                        <field name="NUM">1</field>\
                                      </shadow>\
                                      <block type="variables_get" id="Yq9ZxL*vWiFp~]hg@*f%">\
                                        <field name="VAR" id="Zq^k3oEZ=;$=$VbJ9wYd" variabletype="">i</field>\
                                      </block>\
                                    </value>\
                                    <value name="B">\
                                      <shadow type="math_number" id="Q[V)B=E-ue;o(eCj6%Jc">\
                                        <field name="NUM">1</field>\
                                      </shadow>\
                                    </value>\
                                  </block>\
                                </value>\
                              </block>\
                            </next>\
                          </block>\
                        </next>\
                      </block>\
                    </next>\
                  </block>\
                </next>\
              </block>\
            </statement>\
          </block>\
        </next>\
      </block>\
    </next>\
  </block>\
</xml>';