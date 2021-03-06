package com.example.bootpaytest;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.util.Enumeration;

import kr.co.bootpay.Bootpay;
import kr.co.bootpay.BootpayAnalytics;
import kr.co.bootpay.enums.Method;
import kr.co.bootpay.enums.PG;
import kr.co.bootpay.enums.UX;
import kr.co.bootpay.listener.CancelListener;
import kr.co.bootpay.listener.CloseListener;
import kr.co.bootpay.listener.ConfirmListener;
import kr.co.bootpay.listener.DoneListener;
import kr.co.bootpay.listener.ErrorListener;
import kr.co.bootpay.listener.ReadyListener;
import kr.co.bootpay.model.BootExtra;
import kr.co.bootpay.model.BootUser;
public class MainActivity extends AppCompatActivity {
    private int stuck = 10;
    private View a;
    private TextView ip;
    private String price;
    private String host_port="8888";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        price = "";
        a = findViewById(R.id.view);
        ip=findViewById(R.id.ipadd);

        Thread desktopServerThread = new Thread(new TCPServer());
        desktopServerThread.start();

        ip.setText(getLocalIpAddress());

        BootpayAnalytics.init(this, "5f7c68414f74b40020740718");
    }

    public class TCPServer implements Runnable {

        public static final int ServerPort = 8888;
        public static final String ServerIP = "";

        @Override
        public void run() {

            try {
                System.out.println("S: Connecting...");
                ServerSocket serverSocket = new ServerSocket(ServerPort);

                while (true) {
                    Socket client = serverSocket.accept();
                    System.out.println("S: Receiving...");
                    try {
                        BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                        String str = in.readLine();
                        System.out.println("S: Received: '" + str + "'");
                        price=str;

                        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(client.getOutputStream())), true);
                        out.println("Server Received " + str);

                        OutputStream outmsg = client.getOutputStream();
                        String myMessage="";
                        //myMessage="Server get Price";
                        //outmsg.write(myMessage.getBytes());

                        onClick_request(a);
                    } catch (Exception e) {
                        System.out.println("S: Error");
                        e.printStackTrace();
                    } finally {
                        client.close();
                        System.out.println("S: Done.");
                    }
                }
            } catch (Exception e) {
                System.out.println("S: Error");
                e.printStackTrace();
            }
        }
    }


    public static String getLocalIpAddress() {
        try {
            for (Enumeration<NetworkInterface> en = NetworkInterface.getNetworkInterfaces(); en.hasMoreElements();) {
                NetworkInterface intf = en.nextElement();
                for (Enumeration<InetAddress> enumIpAddr = intf.getInetAddresses(); enumIpAddr.hasMoreElements();) {
                    InetAddress inetAddress = enumIpAddr.nextElement();
                    if (!inetAddress.isLoopbackAddress() && inetAddress instanceof Inet4Address) {
                        return inetAddress.getHostAddress();
                    }
                }
            }
        } catch (SocketException ex) {
            ex.printStackTrace();
        }
        return null;
    }

    public void onClick_request(View v) {
        // ????????????
        BootUser bootUser = new BootUser().setPhone("010-1234-5678");
        BootExtra bootExtra = new BootExtra().setPopup(1);

        Bootpay.init(getFragmentManager())
                .setApplicationId("5f7c68414f74b40020740718") // ?????? ????????????(???????????????)??? application id ???
                .setPG(PG.INICIS) // ????????? PG ???
                .setMethod(Method.PHONE) // ????????????
                .setContext(this)
                .setBootUser(bootUser)
                .setBootExtra(bootExtra)
                .setUX(UX.PG_DIALOG)
//                .setUserPhone("010-1234-5678") // ????????? ????????????
                .setName("ICETmarket") // ????????? ?????????
                .setOrderId("1234") // ?????? ???????????? expire_month
                .setPrice(Integer.parseInt(price)) // ????????? ??????
                //.addItem("??????'s ???", 1, "ITEM_CODE_MOUSE", price) // ??????????????? ?????? ????????????, ????????? ?????? ??????
                //.addItem("?????????", 1, "ITEM_CODE_KEYBOARD", 200, "??????", "????????????", "????????????") // ??????????????? ?????? ????????????, ????????? ?????? ??????
                .onConfirm(new ConfirmListener() { // ????????? ???????????? ?????? ?????? ???????????? ?????????, ?????? ???????????? ?????? ????????? ??????
                    @Override
                    public void onConfirm(@Nullable String message) {

                        if (0 < stuck) Bootpay.confirm(message); // ????????? ?????? ??????.
                        else Bootpay.removePaymentWindow(); // ????????? ?????? ????????? ???????????? ?????? ?????? ??????
                        Log.d("confirm", message);
                    }
                })
                .onDone(new DoneListener() { // ??????????????? ??????, ????????? ?????? ??? ????????? ????????? ????????? ???????????????
                    @Override
                    public void onDone(@Nullable String message) {
                        Log.d("done", message);
                    }
                })
                .onReady(new ReadyListener() { // ???????????? ?????? ??????????????? ???????????? ???????????? ???????????????.
                    @Override
                    public void onReady(@Nullable String message) {
                        Log.d("ready", message);
                    }
                })
                .onCancel(new CancelListener() { // ?????? ????????? ??????
                    @Override
                    public void onCancel(@Nullable String message) {

                        Log.d("cancel", message);
                    }
                })
                .onError(new ErrorListener() { // ????????? ????????? ???????????? ??????
                    @Override
                    public void onError(@Nullable String message) {
                        Log.d("error", message);
                    }
                })
                .onClose(
                        new CloseListener() { //???????????? ????????? ???????????? ??????
                            @Override
                            public void onClose(String message) {
                                Log.d("close", "close");
                            }
                        })
                .request();
    }
}