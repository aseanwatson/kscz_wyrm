module udp_panel_writer
    #(parameter PORT_MSB = 8'h80)
    (input  wire          clk,
    input  wire          reset,
    input  wire          udp_source_valid,
    input  wire          udp_source_last,
    output reg           udp_source_ready,
    input  wire  [15:0]  udp_source_src_port,
    input  wire  [15:0]  udp_source_dst_port,
    input  wire  [31:0]  udp_source_ip_address,
    input  wire  [15:0]  udp_source_length,
    input  wire  [31:0]  udp_source_data,
    input  wire  [3:0]   udp_source_error,
    
    output reg [7:0]     ctrl_en,
    output reg [15:0]    ctrl_addr,
    output reg [23:0]    ctrl_wdat,
    
    output reg led_reg
);

localparam STATE_WAIT_PACKET = 2'b01, STATE_READ_DATA = 2'b10;

reg [7:0] panel_en_mask;
reg [1:0] udp_state;

initial panel_en_mask <= 1'b0;
initial led_reg <= 1'b0;

always @(posedge clk) begin
    if (reset) begin
        udp_state <= STATE_WAIT_PACKET;
        udp_source_ready <= 1'b0;
        led_reg   <= 1'b1;
        ctrl_addr <= 16'b0;
        ctrl_wdat <= 24'b0;
        ctrl_en   <= 8'b0;
        panel_en_mask <= 8'b0;
    end else begin
        udp_source_ready <= 1'b1;
        case (udp_state)
            STATE_WAIT_PACKET : begin
                if (udp_source_valid & (udp_source_dst_port[15:8] == PORT_MSB)) begin
                    ctrl_en <= 8'b0;
                    panel_en_mask <= udp_source_data[7:0];
                    led_reg <= 1'b1;
                    udp_state <= STATE_READ_DATA;
                end
            end
            STATE_READ_DATA : begin
                if (udp_source_valid & (udp_source_dst_port[15:8] == PORT_MSB)) begin
                    ctrl_en          <= panel_en_mask;
                    ctrl_addr        <= {udp_source_data[7:0], udp_source_data[15:10]};
                    ctrl_wdat[23:16] <= {udp_source_data[9:8], udp_source_data[23:20]};
                    ctrl_wdat[15:8]  <= {udp_source_data[19:16], udp_source_data[31:30]};
                    ctrl_wdat[7:0]   <= udp_source_data[29:24];

                    if (udp_source_last) begin
                        panel_en_mask <= 8'b0;
                        udp_state <= STATE_WAIT_PACKET;
                        led_reg <= 1'b0;
                    end
                end
            end
        endcase
    end
end

endmodule
